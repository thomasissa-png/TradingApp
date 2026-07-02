"""TradingApp v3 — Cache « dernière valeur valide » des critères à source réseau.

Problème résolu (incident du 2026-06-25 7h) : une panne réseau ponctuelle d'une
source LENTE (Open-Meteo, FRED, EIA, CFTC, Eurostat…) faisait tomber un critère
en n/a, ce qui pouvait écarter l'actif le plus convaincu du jour (cacao : météo
poids 11 tombée en n/a sur `net_error` Open-Meteo → couverture 41 % < 70 % →
cacao classé « fragile » et écarté du Top 3 alors qu'il a fait +7,13 %).

Solution : à chaque run où un critère ÉLIGIBLE est résolu avec SUCCÈS, on
mémorise sa dernière bonne valeur dans `data/criteres-last-good.json`. Quand la
résolution échoue (handler renvoie None pour cause réseau/429/vide), AVANT de
tomber en n/a, on relit ce cache : si une dernière bonne valeur existe ET est
FRAÎCHE (âge ≤ LAST_GOOD_MAX_AGE_DAYS jours OUVRÉS), on la RÉUTILISE en la
marquant `reporte: true` (échec VISIBLE). Sinon n/a, comportement actuel.

RED LINE (zéro invention) : le cache ne stocke QUE des valeurs RÉELLEMENT
observées lors d'un run réussi. Cache vide ou périmé → n/a. On ne FABRIQUE jamais
une valeur, on ne fait que REJOUER la dernière valeur vraie et récente, et on le
DIT (drapeau + âge + cause de l'échec source).

Périmètre : réservé aux critères à source réseau LENTE (météo, taux, stocks,
COT, balance commerciale…), où une valeur de J-3 reste pertinente. Les familles
PRIX / MOMENTUM / VOLATILITÉ intraday (Twelve/CBOE : momentum, RSI, niveaux VIX,
term structure, gap RV/IV) sont EXCLUES : elles bougent trop vite (une valeur
périmée serait trompeuse et dangereuse) et disposent déjà de leur propre fallback
(Twelve → Stooq). Voir `is_last_good_eligible`.
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("last_good_cache")

ROOT = Path(__file__).resolve().parents[1]
LAST_GOOD_PATH = ROOT / "data" / "criteres-last-good.json"

# Plafond de fraîcheur PAR DÉFAUT d'une valeur reportée, en jours OUVRÉS
# (lundi-vendredi). Au-delà, on retombe en n/a (donnée trop vieille). Sert de
# fallback aux familles non listées dans LAST_GOOD_MAX_AGE_DAYS_BY_TYPE.
LAST_GOOD_MAX_AGE_DAYS: int = 5

# Plafonds d'âge PAR TYPE de critère (verdict panel 3 experts 2026-06-25, 9,3/10).
# Une valeur structurelle lente (COT hebdo) tolère plus de retard qu'un taux ou un
# change qui bougent vite. Au-delà du plafond → la valeur reportée EXPIRE → n/a
# (pas de valeur zombie). Résolution par PRÉFIXE/fragment de cle_courante, du plus
# spécifique au plus générique ; sinon le défaut ci-dessus.
LAST_GOOD_MAX_AGE_DAYS_BY_TYPE: Dict[str, int] = {
    "meteo": 5,                 # anomalies précipitations (Open-Meteo)
    "cftc": 8,                  # positionnement COT (publié hebdo le vendredi)
    "differentiel_taux": 3,     # différentiels de taux (FRED + ECB) — bougent vite
    "taux": 3,                  # taux/rates génériques
    "fx": 3,                    # change / FX
    "balance_commerciale": 5,   # Eurostat (mensuel, structurel)
    "caixin_pmi": 5,            # PMI Chine (mensuel)
}

# Mapping fragment de clé → famille de plafond (pour les clés dont le préfixe ne
# correspond pas littéralement à une entrée ci-dessus, ex. un spread FRED).
_TYPE_BY_KEY_FRAGMENT = (
    ("meteo_", "meteo"),
    ("cftc_", "cftc"),
    ("differentiel_taux", "differentiel_taux"),
    ("balance_commerciale", "balance_commerciale"),
    ("caixin_pmi", "caixin_pmi"),
    ("eurusd", "fx"),
    ("_fx", "fx"),
    ("tips", "taux"),
    ("oas", "taux"),
    ("spread", "taux"),
    ("dxy", "fx"),
    ("oat", "taux"),
    ("bund", "taux"),
)


def max_age_for(cle: str, crit: Optional[dict] = None) -> int:
    """Plafond d'âge (jours ouvrés) applicable au critère `cle`.

    Résolution : fragment de clé connu → famille → plafond ; mot-clé de source
    FRED/ECB → taux ; sinon défaut. Zéro effet de bord.
    """
    low = (cle or "").lower()
    for frag, family in _TYPE_BY_KEY_FRAGMENT:
        if frag in low:
            return LAST_GOOD_MAX_AGE_DAYS_BY_TYPE.get(family, LAST_GOOD_MAX_AGE_DAYS)
    source = (crit.get("source") or "").lower() if crit else ""
    if "fred" in source or "ecb" in source:
        return LAST_GOOD_MAX_AGE_DAYS_BY_TYPE.get("taux", LAST_GOOD_MAX_AGE_DAYS)
    return LAST_GOOD_MAX_AGE_DAYS

# ---------------------------------------------------------------------------
# Périmètre : quels critères peuvent être reportés depuis le cache ?
# ---------------------------------------------------------------------------
#
# INCLUSION (positif) : familles de sources réseau LENTES où une valeur de J-N
# reste pertinente (la donnée elle-même bouge à l'échelle du jour/de la semaine).
# On inclut par préfixe de clé OU par mot-clé de source.
#
# EXCLUSION (garde dure, prioritaire sur l'inclusion) : familles PRIX / MOMENTUM
# / VOL intraday — une valeur périmée y serait trompeuse, et elles ont déjà leur
# propre fallback (Twelve → Stooq). Préfixes/fragments de clé exclus.

# Fragments de clé qui DISQUALIFIENT le repli (prix/momentum/vol rapides).
_EXCLUDE_KEY_FRAGMENTS = (
    "momentum_prix_",      # tendance-prix 7j/20j (tous actifs)
    "rsi_",                # RSI 14j
    "niveau_vix",          # niveau VIX absolu
    "vix_regime",          # régime VIX (mapping non-monotone)
    "vix_risk_off",        # proxy risk-off VIX
    "term_structure",      # term structure VIX / pétrole
    "brent_term",          # term structure Brent
    "gap_rv_iv",           # écart vol réalisée / implicite
    "vvix",                # vol de la vol
)

# Fragments de clé / source qui AUTORISENT le repli (sources réseau lentes).
# Le COT (CFTC) est hebdomadaire (publié le vendredi) : une valeur de quelques
# jours est par nature la valeur courante → repli légitime, y compris cftc_vix.
_INCLUDE_KEY_FRAGMENTS = (
    "meteo_",              # anomalies précipitations (Open-Meteo)
    "cftc_",               # positionnement COT (hebdo)
    "differentiel_taux",   # différentiels de taux (FRED + ECB)
    "balance_commerciale", # Eurostat
    "caixin_pmi",          # Caixin PMI Chine
)
# Mots-clés de SOURCE (champ `source` de la fiche) qui autorisent le repli.
_INCLUDE_SOURCE_FRAGMENTS = (
    "open-meteo", "meteo", "fred", "eia", "cftc", "eurostat", "ecb",
)
# Normalisations « réseau lent » typiques (composite = sous-sources météo/COT).
_INCLUDE_NORMS = ("composite",)


def is_last_good_eligible(cle: str, crit: dict) -> bool:
    """Le critère `cle` peut-il être reporté depuis le cache last-good ?

    True UNIQUEMENT pour les sources réseau LENTES (météo, taux, stocks, COT,
    balance commerciale, PMI). Les familles prix/momentum/vol intraday sont
    exclues (garde dure prioritaire). Zéro effet de bord.
    """
    if not cle:
        return False
    low = cle.lower()
    # Garde dure d'exclusion (prioritaire) : prix / momentum / vol intraday.
    if any(frag in low for frag in _EXCLUDE_KEY_FRAGMENTS):
        return False
    # Inclusion par clé.
    if any(frag in low for frag in _INCLUDE_KEY_FRAGMENTS):
        return True
    # Inclusion par source déclarée dans la fiche.
    source = (crit.get("source") or "").lower()
    if any(frag in source for frag in _INCLUDE_SOURCE_FRAGMENTS):
        return True
    # Inclusion par normalisation (composite = météo + COT, sources lentes).
    norm = (crit.get("normalisation") or "").lower()
    if norm in _INCLUDE_NORMS:
        return True
    return False


# ---------------------------------------------------------------------------
# Persistance du cache JSON
# ---------------------------------------------------------------------------

def load_cache(path: Path = LAST_GOOD_PATH) -> Dict[str, Any]:
    """Charge le cache last-good. {} si absent ou illisible (dégradation sûre)."""
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return data
    except FileNotFoundError:
        return {}
    except Exception as e:  # noqa: BLE001
        logger.warning("cache last-good illisible (%s) — ignoré (n/a comme avant)", e)
    return {}


def save_cache(cache: Dict[str, Any], path: Optional[Path] = None) -> None:
    """Écrit le cache last-good (JSON trié, stable pour le diff git).

    `path=None` → constante module résolue dynamiquement (monkeypatch en test →
    zéro pollution de v3/data)."""
    if path is None:
        path = LAST_GOOD_PATH  # global module → monkeypatch effectif en test
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _entry_from_value(val: dict, run_date: date) -> Optional[Dict[str, Any]]:
    """Construit l'entrée cache à partir d'un dict de valeur résolu avec succès.

    Ne mémorise QUE les champs numériques réellement présents (zéro invention).
    None si le dict ne porte aucune valeur numérique exploitable (rien à cacher).
    """
    entry: Dict[str, Any] = {"date": run_date.isoformat()}
    has_value = False
    for k in ("valeur", "valeur_normalisee", "valeur_ponderee"):
        if k in val and isinstance(val[k], (int, float)):
            entry[k] = float(val[k])
            has_value = True
    return entry if has_value else None


def remember(cache: Dict[str, Any], cle: str, val: dict, run_date: date) -> None:
    """Mémorise la dernière bonne valeur d'un critère résolu (mutation in place).

    On n'écrase l'entrée que si la valeur courante est réellement valide ET
    n'est pas elle-même une valeur reportée (on ne cache jamais un report — sinon
    l'âge se réinitialiserait artificiellement et masquerait la panne durable).
    """
    if not cle or not isinstance(val, dict):
        return
    if val.get("reporte"):
        return
    entry = _entry_from_value(val, run_date)
    if entry is None:
        return
    cache[cle] = entry


def _business_days_between(d_old: date, d_now: date) -> int:
    """Nombre de jours OUVRÉS (lundi-vendredi) strictement entre d_old et d_now.

    Compte les jours ouvrés écoulés depuis la date de la valeur cachée. Un report
    posé vendredi et relu lundi = 0 jour ouvré d'écart (week-end neutralisé), ce
    qui est correct pour une donnée hebdo/quotidienne (marchés fermés le week-end).
    Si d_now <= d_old (cache plus récent ou même jour) → 0.
    """
    if d_now <= d_old:
        return 0
    count = 0
    cur = d_old
    while cur < d_now:
        cur = cur + timedelta(days=1)
        if cur.weekday() < 5:  # 0=lundi … 4=vendredi
            count += 1
    return count


def lookup_fresh(
    cache: Dict[str, Any],
    cle: str,
    now: datetime,
    crit: Optional[dict] = None,
    max_age_days: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """Retourne l'entrée cache si elle existe ET est FRAÎCHE (âge ≤ plafond du
    TYPE de critère, jours ouvrés), enrichie de `age_business_days` et
    `max_age_days`. None sinon (vide/périmé → la valeur reportée EXPIRE).

    `now` : datetime du run (UTC de préférence). La fraîcheur se mesure en jours
    ouvrés écoulés depuis la `date` de l'entrée. `max_age_days` force le plafond
    (sinon résolu par type via max_age_for).
    """
    if max_age_days is None:
        max_age_days = max_age_for(cle, crit)
    entry = cache.get(cle)
    if not isinstance(entry, dict):
        return None
    raw_date = entry.get("date")
    if not raw_date:
        return None
    try:
        d_old = date.fromisoformat(str(raw_date))
    except ValueError:
        return None
    d_now = now.astimezone(timezone.utc).date() if now.tzinfo else now.date()
    age = _business_days_between(d_old, d_now)
    if age > max_age_days:
        return None
    out = dict(entry)
    out["age_business_days"] = age
    out["max_age_days"] = max_age_days
    return out
