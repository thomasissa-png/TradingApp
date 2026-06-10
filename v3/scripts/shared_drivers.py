"""Drivers macro partagés — Reco A de l'audit corrélation cachée (2026-06-05).

Mode AFFICHAGE + LOG UNIQUEMENT (flag-only). Ce module ne touche NI les scores,
NI les conclusions, NI la mesure, NI les gates, NI la couverture. Il lit les
contributions DÉJÀ calculées par le scoring et identifie, run par run, les
critères macro qui portent plusieurs cellules de même direction — pour que le
trader voie d'un coup d'œil quand un « large consensus » est en réalité UN seul
pari macro répliqué (réf. `v3/audit/correlation-cachee-2026-06-05.md`).

Détection 100 % GÉNÉRIQUE (leçon L023) : on raisonne par `cle_courante` (jamais
par nom d'affichage), à partir des contributions réelles du run. Aucune liste
d'actifs ni de critères en dur. Zéro invention : une cellule sans donnée
(is_na / is_gate / valeur absente) ne compte PAS comme « présente ».
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# Part minimale de la contribution d'un driver dans le |score| d'une cellule
# pour que cette cellule soit considérée « portée » par ce driver. Aligné sur
# le seuil de l'audit (Reco A / §2.2 : « ≥ 50 % du score ») et cohérent avec
# MONO_CRITERE_RATIO du scoring (0.50).
DRIVER_PART_MIN: float = 0.50

# Nombre minimal de cellules de MÊME direction portées par le même driver pour
# déclencher un signalement (réf. brief : « ≥ 2 cellules de même direction »).
DRIVER_MIN_CELLULES: float = 2

# Libellés trader (refonte wording 06/06 — pas d'acronyme cru). Clé = cle_courante.
# OPTIONNEL : si une clé partagée n'est pas dans ce map, on retombe sur le `nom`
# du critère (zéro invention — pas de driver inventé, pas de clé masquée).
_DRIVER_LABELS: Dict[str, str] = {
    "taux_10y_us_reels_tips": "Taux réels US (TIPS)",
    "dxy_trend_20j": "Dollar (DXY)",
    "hy_credit_spread": "Spread crédit HY",
    "caixin_pmi_manuf": "PMI manufacturier Chine (Caixin)",
}


def driver_label(cle: str, nom_fallback: str = "") -> str:
    """Libellé trader d'un driver, par `cle_courante`.

    Retombe sur le `nom` du critère si la clé n'est pas mappée, puis sur la clé
    brute en dernier recours. Jamais d'invention de libellé.
    """
    if cle in _DRIVER_LABELS:
        return _DRIVER_LABELS[cle]
    return nom_fallback or cle


def _cell_driver_parts(criteres: List[Any], horizon: str) -> Dict[str, Tuple[float, int]]:
    """Pour une cellule (liste de critères, un horizon), retourne par
    `cle_courante` la part |contribution| / Σ|contributions| et le signe de la
    contribution du driver.

    Suit la méthode de l'audit (§2.2) : part_driver = |contrib_driver| / |Σ contrib|.
    Exclut gates et critères n/a (contribution neutre, donnée absente). Retourne
    {} si la somme des |contributions| est nulle (aucun contributeur réel).
    """
    somme_abs = 0.0
    par_cle: Dict[str, Tuple[float, int]] = {}  # cle -> (|contrib|, signe_contrib)
    for c in criteres:
        if getattr(c, "is_gate", False) or getattr(c, "is_na", False):
            continue
        cle = getattr(c, "cle_courante", "") or ""
        if not cle:
            continue
        ctr = c.contributions.get(horizon)
        if ctr is None:
            continue
        a = abs(ctr)
        somme_abs += a
        # Agrège par clé (en théorie 1 critère par clé/fiche, mais robuste).
        prev_abs, _ = par_cle.get(cle, (0.0, 0))
        signe = 1 if ctr > 0 else (-1 if ctr < 0 else 0)
        par_cle[cle] = (prev_abs + a, signe)
    if somme_abs <= 0.0:
        return {}
    return {cle: (a / somme_abs, signe) for cle, (a, signe) in par_cle.items()}


def compute_cell_shared_drivers(
    actif_result: Any,
    horizon: str,
    cles_partagees: set,
) -> List[Dict[str, Any]]:
    """Champ shadow par cellule : liste des drivers PARTAGÉS qui portent cette
    cellule au-delà de DRIVER_PART_MIN.

    `cles_partagees` = ensemble des cle_courante présentes (donnée réelle) dans
    ≥ 2 fiches sur ce run — calculé une fois par run (cf. `compute_shared_cles`).
    Une cellule n'est concernée par un driver QUE si ce driver est partagé ET
    porte ≥ DRIVER_PART_MIN de son |score|.

    Retourne une liste de dicts {cle, part, signe} (vide si rien). Requêtable
    dans le decision-log. NE MODIFIE RIEN.
    """
    out: List[Dict[str, Any]] = []
    parts = _cell_driver_parts(actif_result.criteres, horizon)
    for cle, (part, signe) in parts.items():
        if cle not in cles_partagees:
            continue
        if part >= DRIVER_PART_MIN:
            out.append({"cle": cle, "part": round(part, 4), "signe": signe})
    # Tri décroissant par part (driver dominant en tête) — stable, déterministe.
    out.sort(key=lambda d: (-d["part"], d["cle"]))
    return out


def compute_shared_cles(results: List[Any], horizons: Tuple[str, ...]) -> set:
    """Ensemble des `cle_courante` présentes (donnée réelle, non n/a, non gate)
    dans ≥ 2 fiches DISTINCTES sur ce run.

    Critère de « présence » : au moins un horizon où la contribution existe
    (valeur non-None) — i.e. le critère a une `valeur_norm` exploitable. On
    compte les FICHES distinctes, pas les cellules : un même critère sur 3
    horizons d'un seul actif n'est pas « partagé ».
    """
    fiches_par_cle: Dict[str, set] = {}
    for r in results:
        for c in r.criteres:
            if getattr(c, "is_gate", False) or getattr(c, "is_na", False):
                continue
            cle = getattr(c, "cle_courante", "") or ""
            if not cle:
                continue
            present = any(c.contributions.get(h) is not None for h in horizons)
            if not present:
                continue
            fiches_par_cle.setdefault(cle, set()).add(r.nom)
    return {cle for cle, fiches in fiches_par_cle.items() if len(fiches) >= 2}


def compute_shared_drivers_summary(
    results: List[Any],
    horizons: Tuple[str, ...],
) -> List[Dict[str, Any]]:
    """Synthèse run : pour chaque driver partagé qui porte ≥ DRIVER_MIN_CELLULES
    cellules de MÊME direction, agrège les actifs concernés.

    Direction d'une cellule portée = signe de la contribution du driver dans la
    cellule (LONG si +1, SHORT si -1). On groupe par (cle, direction) : un même
    driver peut être SHORT sur N actifs et LONG sur d'autres (rare, mais on ne
    fusionne pas des directions opposées — sinon le message tromperait).

    Retourne une liste de dicts triée par n_cellules décroissant :
        {cle, label, direction ("LONG"/"SHORT"), actifs (set→list triée),
         n_cellules, n_actifs, part_max}
    Vide si aucun driver ne dépasse le seuil → le bloc bulletin ne s'affiche pas.
    """
    cles_partagees = compute_shared_cles(results, horizons)
    if not cles_partagees:
        return []

    # (cle, direction) -> agrégat
    agg: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for r in results:
        for h in horizons:
            parts = _cell_driver_parts(r.criteres, h)
            label_par_cle = {
                (getattr(c, "cle_courante", "") or ""): c.nom for c in r.criteres
            }
            for cle, (part, signe) in parts.items():
                if cle not in cles_partagees or part < DRIVER_PART_MIN or signe == 0:
                    continue
                direction = "LONG" if signe > 0 else "SHORT"
                key = (cle, direction)
                entry = agg.setdefault(
                    key,
                    {
                        "cle": cle,
                        "label": driver_label(cle, label_par_cle.get(cle, "")),
                        "direction": direction,
                        "actifs": set(),
                        "n_cellules": 0,
                        "part_max": 0.0,
                    },
                )
                entry["actifs"].add(r.nom)
                entry["n_cellules"] += 1
                if part > entry["part_max"]:
                    entry["part_max"] = part

    out: List[Dict[str, Any]] = []
    for entry in agg.values():
        if entry["n_cellules"] < DRIVER_MIN_CELLULES:
            continue
        actifs_tries = sorted(entry["actifs"])
        out.append(
            {
                "cle": entry["cle"],
                "label": entry["label"],
                "direction": entry["direction"],
                "actifs": actifs_tries,
                "n_cellules": entry["n_cellules"],
                "n_actifs": len(actifs_tries),
                "part_max": round(entry["part_max"], 4),
            }
        )
    # Tri : plus de cellules d'abord, puis part_max, puis label (déterministe).
    out.sort(key=lambda d: (-d["n_cellules"], -d["part_max"], d["label"]))
    return out


# Symbole de la légende compacte (réf. audit Reco A : ⚭).
SHARED_DRIVERS_SYMBOL: str = "⚭"


def build_shared_drivers_block(summary: List[Dict[str, Any]]) -> List[str]:
    """Construit le bloc markdown « ⚭ Drivers macro partagés ».

    Langage trader, court. Une ligne par driver partagé signalé. Si `summary`
    est vide → retourne [] (PAS de bloc, pas de bruit). À placer près de la
    synthèse / « cellules à surveiller ».
    """
    if not summary:
        return []
    lines: List[str] = []
    lines.append(f"## {SHARED_DRIVERS_SYMBOL} Drivers macro partagés")
    lines.append("")
    lines.append(
        "_Un même driver macro porte plusieurs cellules de même direction : "
        "ce ne sont pas N convictions indépendantes mais UN pari répété. "
        "Un retournement de ce driver les fausserait ensemble._"
    )
    lines.append("")
    for d in summary:
        actifs_str = " / ".join(d["actifs"])
        lines.append(
            f"- {SHARED_DRIVERS_SYMBOL} {d['label']} : porte {d['n_cellules']} "
            f"cellules {d['direction']} ({actifs_str}) — un retournement de ce "
            f"driver les fausserait ensemble."
        )
    lines.append("")
    return lines
