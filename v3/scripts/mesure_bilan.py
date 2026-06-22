"""Mesure AUTO-SUFFISANTE du « Bilan du jour » — fenêtre = JOUR DE BOURSE MÊME.

Refonte 2026-06 (défaut de conception corrigé). Avant : `build_bilan_jour`
déléguait à `journaliste.measure(today=compute_echeance(date_j, "24h"))`, soit
le PROCHAIN jour ouvré. À 22h15 le soir J, la clôture du jour d'échéance (J+1)
n'existe pas → toutes les cellules sortaient « non-notee » sans même tenter un
fetch. C'était un défaut STRUCTUREL, pas un fetch raté.

Après : on mesure nous-mêmes la journée J pour chaque call 7h, sur le MÊME jour
(ouverture du jour → clôture du même jour ~22h). On capture :

- **Référence** = prix d'OUVERTURE du jour (réutilise
  `journaliste._resolve_prix_reference` : ouverture marché, fallback émission 7h).
- **Clôture** = prix à `now` (~22h15) via une CASCADE de fallback :
  bougie 1day du jour → dernière barre 1h → spot fetch_price →
  dernier relevé de suivi (run_suivi) → sinon non-notee « donnée absente ».
- **Max favorable / adverse** sur la séance : excursions sur la série 1h intraday
  (extrema des close des barres du jour J). Favorable = dans le sens du call.
- **Résultat** VRAI/FAUSSE/NC : RÉUTILISE `journaliste.measure_cell` (seuils
  identiques, zéro réinvention).

Zéro invention de donnée : toute source absente reste « — » / n/a, jamais comblée.
Best-effort : aucune exception ne doit faire crasher le bilan (try/except qui
dégrade proprement).

Injection des fetchers (callables) → testable sans réseau.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

PARIS_TZ = ZoneInfo("Europe/Paris")

# Sources possibles du cours de clôture (ordre de la cascade).
CLOTURE_1DAY = "1day"
CLOTURE_1H = "1h"
CLOTURE_SPOT = "spot"
CLOTURE_SUIVI = "suivi"

# Type d'un fetcher de série : (symbol, *, interval, outputsize) -> [(dt, close)]|None
SeriesFetcher = Callable[..., Optional[List[Tuple[datetime, float]]]]
# Type d'un fetcher de prix spot : (symbol) -> float|None
PriceFetcher = Callable[[str], Optional[float]]


def _to_paris_date(dt: datetime) -> date:
    """Date Paris d'un datetime (tz-aware ou naïf supposé UTC)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(PARIS_TZ).date()


def _bars_du_jour(
    series: Optional[List[Tuple[datetime, float]]],
    date_j: date,
) -> List[Tuple[datetime, float]]:
    """Garde uniquement les barres dont la date Paris == date_j, triées oldest→newest."""
    if not series:
        return []
    bars = [(dt, px) for dt, px in series if _to_paris_date(dt) == date_j]
    bars.sort(key=lambda t: t[0])
    return bars


def _excursions_intraday(
    bars: List[Tuple[datetime, float]],
    reference: float,
    call: str,
) -> Tuple[Optional[float], Optional[float]]:
    """Excursions FAVORABLE max et ADVERSE max sur la série 1h du jour.

    Calculées en % vs `reference` (prix d'ouverture). « Favorable » = dans le sens
    du call (LONG → hausse, SHORT → baisse). On parcourt les close des barres du
    jour (Twelve `fetch_twelve_series` ne sert que des close, pas de high/low intra
    -barre → on utilise l'extrême des close, approximation honnête et documentée).

    Retourne (max_favorable_pct >= 0, max_adverse_pct <= 0). (None, None) si pas
    de barre exploitable ou référence invalide. Zéro invention.
    """
    from run_suivi import call_sign  # noqa: PLC0415

    sign = call_sign(call)
    if sign is None or not reference or reference <= 0 or not bars:
        return (None, None)

    fav_max: Optional[float] = None
    adv_max: Optional[float] = None
    for _dt, px in bars:
        if not isinstance(px, (int, float)) or px <= 0:
            continue
        delta_pct = (px - reference) / reference * 100.0
        fav = delta_pct * sign  # signé dans le sens du call
        if fav_max is None or fav > fav_max:
            fav_max = fav
        if adv_max is None or fav < adv_max:
            adv_max = fav
    if fav_max is None:
        return (None, None)
    # Normalise : favorable = part positive de l'excursion (0 si jamais positif) ;
    # adverse = part négative (0 si jamais négatif). On expose les EXTREMA bruts
    # signés-favorable pour que l'appelant lise « meilleur point / pire point ».
    favorable = max(fav_max, 0.0)
    adverse = min(adv_max if adv_max is not None else 0.0, 0.0)
    return (round(favorable, 4), round(adverse, 4))


def _resolve_cloture(
    ticker: str,
    date_j: date,
    series_1day: Optional[List[Tuple[datetime, float]]],
    series_1h: Optional[List[Tuple[datetime, float]]],
    fetch_price: Optional[PriceFetcher],
    suivi_cloture: Optional[float],
    suivi_fav_pct: Optional[float] = None,
    reference: Optional[float] = None,
    call: Optional[str] = None,
) -> Tuple[Optional[float], Optional[str], Optional[str]]:
    """Cascade de fallback pour le cours de CLÔTURE du jour J (~22h15).

    Ordre (zéro invention) :
      1. bougie 1day du jour J (close officiel du jour si déjà servi)
      2. dernière barre 1h du jour J
      3. spot via fetch_price(ticker)
      4. dernier relevé de suivi reconstruit (suivi_cloture)
      5. sinon (None, None, None) → l'appelant marque non-notee « donnée absente ».

    Retourne (prix, source, heure_paris|None).
    """
    # 1. bougie 1day du jour
    bars_day = _bars_du_jour(series_1day, date_j)
    if bars_day:
        px = bars_day[-1][1]
        if isinstance(px, (int, float)) and px > 0:
            return (float(px), CLOTURE_1DAY, None)

    # 2. dernière barre 1h du jour
    bars_h = _bars_du_jour(series_1h, date_j)
    if bars_h:
        dt, px = bars_h[-1]
        if isinstance(px, (int, float)) and px > 0:
            heure = dt.astimezone(PARIS_TZ).strftime("%Hh%M") if dt.tzinfo else None
            return (float(px), CLOTURE_1H, heure)

    # 3. spot
    if fetch_price is not None:
        try:
            spot = fetch_price(ticker)
        except Exception as e:  # noqa: BLE001 — best-effort, on dégrade
            logger.warning("mesure_bilan : spot fetch KO %s : %s", ticker, e)
            spot = None
        if isinstance(spot, (int, float)) and spot > 0:
            return (float(spot), CLOTURE_SPOT, None)

    # 4. dernier relevé de suivi
    #    (a) prix absolu fourni directement, ou
    #    (b) reconstruit depuis le dernier fav% (18h/12h) + la référence du jour :
    #        fav = delta * sign ⇒ delta = fav / sign ⇒ prix = ref * (1 + delta/100).
    if isinstance(suivi_cloture, (int, float)) and suivi_cloture > 0:
        return (float(suivi_cloture), CLOTURE_SUIVI, None)
    if (
        isinstance(suivi_fav_pct, (int, float))
        and isinstance(reference, (int, float)) and reference > 0
        and call in ("LONG", "SHORT")
    ):
        from run_suivi import call_sign  # noqa: PLC0415
        sign = call_sign(call)
        if sign is not None:
            delta = suivi_fav_pct / sign
            px = reference * (1.0 + delta / 100.0)
            if px > 0:
                return (float(px), CLOTURE_SUIVI, None)

    # 5. donnée absente
    return (None, None, None)


def measure_cellule_journee(
    cell: Any,
    fiche_key: str,
    fiche: dict,
    *,
    date_j: date,
    prix_emis: Dict[str, float],
    prix_ouverture_dir: Path,
    fetch_series: Optional[SeriesFetcher],
    fetch_price: Optional[PriceFetcher],
    suivi_cloture: Optional[float] = None,
    suivi_fav_pct: Optional[float] = None,
    series_1day: Optional[List[Tuple[datetime, float]]] = None,
    series_1h: Optional[List[Tuple[datetime, float]]] = None,
) -> Any:
    """Mesure UNE cellule 7h sur la journée de bourse J (ouverture → clôture).

    Réutilise :
    - `journaliste._resolve_prix_reference` pour la RÉFÉRENCE (ouverture/émission) ;
    - `journaliste.measure_cell` pour le verdict VRAI/FAUSSE/NC (seuils inchangés).

    Ajoute (champs optionnels de Measure) : max_favorable_pct, max_adverse_pct,
    prix_cloture_source, prix_cloture_heure.

    `series_1day` / `series_1h` peuvent être pré-injectés (tests / cache) ; sinon
    on les fetch via `fetch_series`. Best-effort total : toute erreur → cellule
    non-notee « donnée absente » plutôt qu'un crash ou une invention.
    """
    import journaliste as J  # noqa: PLC0415

    ticker = fiche.get("ticker_principal", "")

    # --- Référence (ouverture du jour, fallback émission) ---
    try:
        reference, ref_source = J._resolve_prix_reference(
            ticker, date_j, prix_emis, prix_ouverture_dir, fiche,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("mesure_bilan : _resolve_prix_reference KO %s : %s", ticker, e)
        reference, ref_source = (None, None)

    # --- Séries intraday (1day pour close officiel, 1h pour excursions + fallback) ---
    if series_1h is None and fetch_series is not None:
        try:
            series_1h = fetch_series(ticker, interval="1h", outputsize=24)
        except Exception as e:  # noqa: BLE001
            logger.warning("mesure_bilan : fetch_series 1h KO %s : %s", ticker, e)
            series_1h = None
    if series_1day is None and fetch_series is not None:
        try:
            series_1day = fetch_series(ticker, interval="1day", outputsize=5)
        except Exception as e:  # noqa: BLE001
            logger.warning("mesure_bilan : fetch_series 1day KO %s : %s", ticker, e)
            series_1day = None

    # --- Clôture (cascade) ---
    call = getattr(cell, "conclusion", "")
    cloture, clot_source, clot_heure = _resolve_cloture(
        ticker, date_j, series_1day, series_1h, fetch_price, suivi_cloture,
        suivi_fav_pct=suivi_fav_pct, reference=reference, call=call,
    )

    # --- Garde-fou COHÉRENCE D'ÉCHELLE (fix indices, brief 2026-06) ---
    # market_data mappe ^GSPC→SPY (~750) et ^IXIC→QQQ (~740), alors que la sonde
    # a confirmé que Grow sert ^GSPC/^IXIC EN DIRECT (~5500 / ~19000) en CI. Si la
    # référence (ouverture) et la clôture viennent d'instruments d'ÉCHELLES
    # DIFFÉRENTES (proxy ETF vs indice direct), un delta = (5500-748)/748 serait
    # absurde. On NE calcule JAMAIS un tel delta : on REFUSE la mesure (échelle
    # incohérente) plutôt que de produire un chiffre faux. Heuristique : ratio
    # clôture/référence hors [1/3 ; 3] = changement d'instrument quasi certain
    # (un actif ne fait jamais ±200 % en une séance).
    echelle_incoherente = False
    if (
        isinstance(reference, (int, float)) and reference > 0
        and isinstance(cloture, (int, float)) and cloture > 0
    ):
        ratio = cloture / reference
        if ratio > 3.0 or ratio < (1.0 / 3.0):
            echelle_incoherente = True
            logger.warning(
                "mesure_bilan : échelle incohérente %s ref=%.4g close=%.4g "
                "(ratio=%.2f) — mesure refusée (proxy vs direct ?)",
                ticker, reference, cloture, ratio,
            )

    # --- Verdict via measure_cell (seuils + logique réutilisés tels quels) ---
    # today=None / prix_courant_date=None → pas de refus prématuré (on mesure le
    # jour même DÉLIBÉRÉMENT, l'échéance 24h jour-ouvré ne s'applique pas ici).
    # Si échelle incohérente : on neutralise la clôture passée à measure_cell pour
    # qu'aucun delta ne soit calculé (cellule non terminale), et on pose une note.
    cloture_for_verdict = None if echelle_incoherente else cloture
    m = J.measure_cell(
        cell=cell,
        fiche_key=fiche_key,
        fiche=fiche,
        prix_emission=reference,
        prix_courant=cloture_for_verdict,
    )
    m.prix_reference_source = ref_source
    m.prix_cloture_source = clot_source
    m.prix_cloture_heure = clot_heure
    if echelle_incoherente:
        m.note = (
            f"échelle incohérente (réf {ref_source or 'n/a'}={reference:.4g} vs "
            f"clôture {clot_source or 'n/a'}={cloture:.4g}) : mesure refusée"
        )
        m.prix_courant = None

    # Note explicite si la clôture est absente (garde-fou honnêteté côté rendu).
    # measure_cell a déjà posé une note « prix courant indisponible » ; on précise
    # seulement si aucune note n'a été posée.
    if cloture is None and not m.note:
        m.note = "clôture indisponible (donnée absente)"

    # --- Excursions intraday (max favorable / adverse) ---
    if reference is not None and call in ("LONG", "SHORT"):
        bars_h = _bars_du_jour(series_1h, date_j)
        fav, adv = _excursions_intraday(bars_h, reference, call)
        m.max_favorable_pct = fav
        m.max_adverse_pct = adv

    return m


def load_cells_et_prix_7h(
    date_j: date,
    bulletins_dir: Path,
    prix_emission_dir: Path,
) -> Tuple[List[Any], Dict[str, float]]:
    """Charge les cellules 24h du Briefing 7h du jour J + le dict ticker→prix d'émission.

    On parcourt les bulletins de `date_j`, on ne garde que les bulletins 7h
    (`is_seven_am_bulletin`) et les cellules d'horizon 24h, conclusion LONG/SHORT.
    Le dict prix d'émission est fusionné sur tous les bulletins 7h du jour
    (clé par identité de bulletin/créneau). Zéro invention : un bulletin manquant
    → liste vide, l'appelant affiche « mesure indisponible ».
    """
    import journaliste as J  # noqa: PLC0415

    cells: List[Any] = []
    prix_emis: Dict[str, float] = {}
    for bpath in J.list_bulletins(bulletins_dir):
        try:
            bcells = J.parse_bulletin(bpath)
        except Exception as e:  # noqa: BLE001
            logger.warning("mesure_bilan : parse_bulletin KO %s : %s", bpath, e)
            continue
        if not bcells:
            continue
        if bcells[0].bulletin_date != date_j:
            continue
        bid = bcells[0].bulletin_id
        if not J.is_seven_am_bulletin(bid):
            continue
        for c in bcells:
            if c.horizon == "24h" and c.conclusion in ("LONG", "SHORT"):
                cells.append(c)
        # Prix d'émission de ce bulletin 7h (fusionnés).
        for k, v in J.load_prix_emission(bid, prix_emission_dir).items():
            prix_emis.setdefault(k, v)
    return cells, prix_emis


def measure_journee_bourse(
    cells: List[Any],
    fiches: Dict[str, dict],
    *,
    date_j: date,
    prix_emis: Dict[str, float],
    prix_ouverture_dir: Path,
    fetch_series: Optional[SeriesFetcher] = None,
    fetch_price: Optional[PriceFetcher] = None,
    suivi_cloture_map: Optional[Dict[str, float]] = None,
    suivi_fav_map: Optional[Dict[str, float]] = None,
) -> List[Any]:
    """Mesure TOUTES les cellules 7h 24h du jour J sur la journée de bourse même.

    `cells` : cellules du Briefing 7h (horizon 24h) à mesurer.
    `prix_emis` : dict ticker → prix d'émission 7h (fallback référence).
    `suivi_cloture_map` : ticker → dernier prix relevé par le suivi (fallback clôture).

    Best-effort par cellule : une cellule en erreur ne fait pas tomber les autres.
    """
    suivi_cloture_map = suivi_cloture_map or {}
    suivi_fav_map = suivi_fav_map or {}
    out: List[Any] = []
    # Cache des séries par ticker (1 fetch par ticker pour tout le bilan).
    cache_1h: Dict[str, Optional[List[Tuple[datetime, float]]]] = {}
    cache_1day: Dict[str, Optional[List[Tuple[datetime, float]]]] = {}

    for cell in cells:
        actif_name = getattr(cell, "actif_name", "")
        pair = None
        try:
            from journaliste import fiche_for_actif_name  # noqa: PLC0415
            pair = fiche_for_actif_name(fiches, actif_name)
        except Exception:  # noqa: BLE001
            pair = None
        if pair is None:
            logger.warning("mesure_bilan : fiche introuvable pour %s — cellule ignorée", actif_name)
            continue
        fiche_key, fiche = pair
        ticker = fiche.get("ticker_principal", "")

        if fetch_series is not None and ticker not in cache_1h:
            try:
                cache_1h[ticker] = fetch_series(ticker, interval="1h", outputsize=24)
            except Exception as e:  # noqa: BLE001
                logger.warning("mesure_bilan : fetch_series 1h KO %s : %s", ticker, e)
                cache_1h[ticker] = None
            try:
                cache_1day[ticker] = fetch_series(ticker, interval="1day", outputsize=5)
            except Exception as e:  # noqa: BLE001
                logger.warning("mesure_bilan : fetch_series 1day KO %s : %s", ticker, e)
                cache_1day[ticker] = None

        try:
            m = measure_cellule_journee(
                cell, fiche_key, fiche,
                date_j=date_j,
                prix_emis=prix_emis,
                prix_ouverture_dir=prix_ouverture_dir,
                fetch_series=fetch_series,
                fetch_price=fetch_price,
                suivi_cloture=suivi_cloture_map.get(ticker),
                suivi_fav_pct=suivi_fav_map.get(ticker),
                series_1day=cache_1day.get(ticker),
                series_1h=cache_1h.get(ticker),
            )
            out.append(m)
        except Exception as e:  # noqa: BLE001 — jamais de crash du bilan
            logger.warning("mesure_bilan : mesure KO %s : %s — cellule sautée", actif_name, e)
            continue
    return out


def persist_mesures_jour(
    measures: List[Any],
    date_j: date,
    measures_log_path: Path,
) -> int:
    """Fusionne les mesures du jour J dans le measures-log (append-only par jour).

    Le measures-log historique est PRÉSERVÉ : on retire seulement les anciennes
    lignes 24h du jour J (dédup par (actif, bulletin_date) pour éviter les doublons
    si le bilan re-tourne), puis on ajoute les nouvelles. Ainsi
    `variations_24h_significatives` (qui lit ce log) cesse d'être vide quand le
    bilan a tourné. Zéro invention : seules les mesures réellement calculées sont
    écrites. Retourne le nombre de lignes ajoutées.

    Idempotent : rejouer le bilan le même jour réécrit ses lignes, pas de doublon.
    """
    import journaliste as J  # noqa: PLC0415

    di = date_j.isoformat()
    # Clés des nouvelles mesures du jour à remplacer.
    new_keys = {
        (getattr(m.cell, "actif_name", None), getattr(m.cell, "bulletin_date", None))
        for m in measures
    }

    kept: List[str] = []
    if measures_log_path.exists():
        import json  # noqa: PLC0415
        for line in measures_log_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            # On retire les anciennes lignes du jour J qui correspondent à une
            # nouvelle mesure (même actif + bulletin_date) ; le reste est conservé.
            if isinstance(r, dict) and r.get("bulletin_date") == di:
                bd = None
                try:
                    bd = date.fromisoformat(di)
                except ValueError:
                    bd = None
                if (str(r.get("actif")), bd) in new_keys and r.get("horizon") == "24h":
                    continue
            kept.append(line)

    import json  # noqa: PLC0415
    added: List[str] = [
        json.dumps(J.measure_to_record(m), ensure_ascii=False) for m in measures
    ]
    measures_log_path.parent.mkdir(parents=True, exist_ok=True)
    all_lines = kept + added
    measures_log_path.write_text(
        "\n".join(all_lines) + ("\n" if all_lines else ""), encoding="utf-8",
    )
    return len(added)


__all__ = [
    "measure_journee_bourse",
    "measure_cellule_journee",
    "persist_mesures_jour",
    "load_cells_et_prix_7h",
    "CLOTURE_1DAY",
    "CLOTURE_1H",
    "CLOTURE_SPOT",
    "CLOTURE_SUIVI",
]
