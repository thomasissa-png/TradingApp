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

# Part minimale POUR LE SIGNALEMENT DE FAUX CONSENSUS (bloc ⚭ « Drivers macro
# partagés »). Plus BASSE que DRIVER_PART_MIN (0.50) : un driver qui pèse 30-49 %
# d'une cellule n'est pas le « driver dominant » affiché en « Porté par », mais il
# crée quand même une CORRÉLATION CACHÉE entre actifs (audit fond 22/06, Analyst :
# le bloc ratait Nasdaq/S&P 7j-1m où les taux réels US pèsent fort sans être >50 %).
# On élargit donc l'AVERTISSEMENT de risque sans toucher l'attribution « Porté par ».
DRIVER_PART_MIN_CONSENSUS: float = 0.30

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


# ---------------------------------------------------------------------------
# Familles macro — dédup de la « Sélection du jour » par FAMILLE de drivers.
# ---------------------------------------------------------------------------
# Défaut démontré (11/06) : la sélection aurait retenu Argent (top-driver
# `taux_10y_us_reels_tips`), EUR/USD (`differentiel_taux_2y_us_de`) et Café —
# trois « paris différents » selon la dédup par `cle_courante`. Or TIPS et écart
# 2Y US-DE sont LE MÊME complexe taux réels / dollar : c'est un seul pari macro
# répliqué. La dédup de SÉLECTION doit donc raisonner par FAMILLE macro, pas par
# critère littéral (réf. brief 12/06).
#
# Ce mapping NE TOUCHE PAS le bloc « À jouer » ni les drivers partagés ⚭ (qui
# restent à la granularité critère, informative). Il sert UNIQUEMENT à la dédup
# de sélection 24h (affichage + decision-log shadow).
#
# Construction 100 % à partir des `cle_courante` RÉELLES des 12 fiches
# (grep cle_courante v3/config/fiches/*.yml) — zéro invention de clé. Toute clé
# ABSENTE de ce mapping retombe en famille SINGLETON (= la clé elle-même) :
# aucun regroupement abusif (leçon L023, zéro invention).
#
# Familles (label trader = motif affiché « même pari (<label>) que <Actif> ») :
#   - taux_dollar      : complexe taux réels / dollar (TIPS, écarts de taux
#                        US-DE 2Y/10Y, variation du 10Y US, dollar DXY, USD/JPY,
#                        FedWatch). L'OAT-Bund est un driver FRANCE → stress_europe.
#   - risk_on_off      : régime de risque (VIX niveau/régime/term structure, V2X,
#                        VXN, VVIX, SKEW, spread crédit HY, put/call).
#   - metaux_croises   : complexe métaux précieux croisé (mouvement de l'or,
#                        ratio or/argent, ratio cuivre/or).
#   - stress_europe    : stress souverain zone euro (OAT-Bund, tension politique FR).
#   - tendance_propre  : PAR-ACTIF (momentum/RSI/breadth/flux de SON propre actif)
#                        → JAMAIS regroupé entre actifs différents (cf. ci-dessous).
#
# tendance_propre est INTRINSÈQUEMENT par-actif : le momentum de l'or et le
# momentum du cacao ne sont PAS le même pari. Ces clés ne sont donc PAS dans la
# table fixe : `famille_macro()` les détecte par préfixe et préfixe la famille
# par la fiche/actif (ex. `tendance_propre:or`) → deux actifs ≠ deux familles.

# Mapping EXACT cle_courante → (famille, label trader). Une seule entrée par clé.
_FAMILLE_EXACTE: Dict[str, Tuple[str, str]] = {
    # --- taux_dollar : complexe taux réels / dollar ---
    "taux_10y_us_reels_tips": ("taux_dollar", "taux/dollar"),
    "differentiel_taux_2y_us_de": ("taux_dollar", "taux/dollar"),
    "differentiel_taux_10y_us_bund": ("taux_dollar", "taux/dollar"),
    "taux_10y_us_delta_5j": ("taux_dollar", "taux/dollar"),
    "dxy_trend_20j": ("taux_dollar", "taux/dollar"),
    "usd_jpy_proxy_risk": ("taux_dollar", "taux/dollar"),
    "fedwatch_proba": ("taux_dollar", "taux/dollar"),
    # --- risk_on_off : régime de risque ---
    "niveau_vix_absolu": ("risk_on_off", "régime de risque"),
    "vix_regime": ("risk_on_off", "régime de risque"),
    "vix_risk_off_proxy": ("risk_on_off", "régime de risque"),
    "term_structure_vix_vix3m": ("risk_on_off", "régime de risque"),
    "v2x_regime": ("risk_on_off", "régime de risque"),
    "vxn_regime": ("risk_on_off", "régime de risque"),
    "vvix": ("risk_on_off", "régime de risque"),
    "skew_index_cboe": ("risk_on_off", "régime de risque"),
    "put_call_ratio_cboe_5j": ("risk_on_off", "régime de risque"),
    "hy_credit_spread": ("risk_on_off", "régime de risque"),
    # --- metaux_croises : complexe métaux précieux croisé ---
    "mouvement_or_5j": ("metaux_croises", "métaux croisés"),
    "flux_etf_or_5j": ("metaux_croises", "métaux croisés"),
    "ratio_gold_silver": ("metaux_croises", "métaux croisés"),
    "ratio_cuivre_or": ("metaux_croises", "métaux croisés"),
    # --- stress_europe : stress souverain zone euro ---
    "spread_oat_bund_10y": ("stress_europe", "stress zone euro"),
    "spread_oat_bund_stress_ez": ("stress_europe", "stress zone euro"),
    "tension_politique_fr": ("stress_europe", "stress zone euro"),
}

# Préfixes des critères de TENDANCE PROPRE (par-actif). La famille est suffixée
# par la fiche/actif → `tendance_propre:<fiche>` (deux actifs ≠ deux familles).
_TENDANCE_PROPRE_PREFIXES: Tuple[str, ...] = (
    "momentum_prix_",
    "rsi_14j_",
    "breadth_",
    "sox_trend",
)
_TENDANCE_PROPRE_LABEL = "tendance propre"


def famille_macro(cle: str, fiche_key: str = "") -> Tuple[str, str]:
    """Famille macro + label trader d'un driver, pour la dédup de SÉLECTION.

    Retourne `(famille, label)` :
      - clé mappée dans `_FAMILLE_EXACTE` → sa famille + son label trader ;
      - clé de tendance propre (préfixe) → `("tendance_propre:<fiche>", ...)`
        afin que deux actifs distincts ne soient JAMAIS regroupés (le momentum
        de l'or et celui du cacao ne sont pas le même pari) ;
      - sinon → SINGLETON : `(cle, cle)`. Aucun regroupement abusif, zéro
        invention de famille (leçon L023).

    `fiche_key` n'est utilisé QUE pour la tendance propre. Si vide pour une clé
    de tendance, on retombe sur la clé brute (singleton de fait) plutôt que de
    fusionner deux actifs à tort.
    """
    if not cle:
        return "", ""
    if cle in _FAMILLE_EXACTE:
        return _FAMILLE_EXACTE[cle]
    for prefixe in _TENDANCE_PROPRE_PREFIXES:
        if cle.startswith(prefixe):
            if fiche_key:
                return (f"tendance_propre:{fiche_key}", _TENDANCE_PROPRE_LABEL)
            return (cle, _TENDANCE_PROPRE_LABEL)
    return (cle, cle)


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
    part_min: float = DRIVER_PART_MIN_CONSENSUS,
) -> List[Dict[str, Any]]:
    """Synthèse run : pour chaque driver partagé qui porte ≥ DRIVER_MIN_CELLULES
    cellules de MÊME direction, agrège les actifs concernés.

    Direction d'une cellule portée = signe de la contribution du driver dans la
    cellule (LONG si +1, SHORT si -1). On groupe par (cle, direction) : un même
    driver peut être SHORT sur N actifs et LONG sur d'autres (rare, mais on ne
    fusionne pas des directions opposées — sinon le message tromperait).

    `part_min` (défaut DRIVER_PART_MIN_CONSENSUS = 0.30) : seuil de part du driver
    dans le |score| d'une cellule pour la compter dans le faux consensus. Plus bas
    que le seuil « Porté par » (0.50) afin de capter les corrélations cachées
    secondaires (ex. taux réels US sur Nasdaq/S&P 7j-1m) — audit fond 22/06.

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
                if cle not in cles_partagees or part < part_min or signe == 0:
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
        # [C-B4 audit visuel 12/06] : bullet unique, langage trader — on nomme
        # le driver, les actifs et la direction, sans la prose redondante
        # « porte N cellule(s) sur M actif(s) » (déjà visible via ⚭ dans le
        # tableau À jouer). Liste lisible : « Nasdaq et Or » plutôt que virgules.
        actifs = list(d["actifs"])
        if len(actifs) > 1:
            actifs_str = ", ".join(actifs[:-1]) + " et " + actifs[-1]
        else:
            actifs_str = actifs[0] if actifs else "—"
        lines.append(
            f"- {SHARED_DRIVERS_SYMBOL} **{d['label']}** : {actifs_str} "
            f"{d['direction']} — un retournement les fausse ensemble."
        )
    lines.append("")
    return lines
