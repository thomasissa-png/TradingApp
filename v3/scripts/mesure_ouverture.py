"""TradingApp v3 — Mesure ouverture→clôture (Phase 1 refonte 5 rapports).

Source de vérité : `v3/docs/reco/spec-refonte-5-rapports.md` §2 (mesure) + §7 (CA-M*).

Ce module ajoute le PRIX DE RÉFÉRENCE = OUVERTURE DE MARCHÉ, distinct du prix
d'émission bulletin. Le modèle de mesure 24h passe de « prix au run 7h » (souvent
marché fermé / pré-ouverture) à « ouverture propre du marché → clôture, jugé à
22h le jour même ».

Concepts :
- Chaque actif appartient à un GROUPE de marché (eu / us / continu) qui définit
  son heure d'ouverture Paris (table §2.2, config `v3/config/suivi.yaml`).
- `stamp_prix_ouverture(date_j, now=...)` stampe le prix d'ouverture de chaque
  actif APRÈS l'ouverture de son marché (+ OPEN_STAMP_DELAY_MIN), dans
  `v3/data/prix-ouverture/{YYYY-MM-DD}.json`. Idempotent + entry-lock.
- Le Journaliste lit ce fichier comme référence pour le 24h (et 7j/1m, Q3).

Garde-fous (non négociables) :
- WIN RATE ONLY — aucune valeur monétaire ici.
- Zéro invention : Twelve KO → ticker absent du JSON → `suivi-interrompu`, retry.
- DST : heures en Europe/Paris via ZoneInfo, JAMAIS d'offset codé en dur.
- Convention 08h des continus = référence conventionnelle (Q10, décision Thomas
  « ouverture propre entre 8h-22h »), PAS du close-to-close. Documenté §2.2.
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from zoneinfo import ZoneInfo

import yaml

logger = logging.getLogger("mesure_ouverture")

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
SUIVI_CONFIG_FILE = CONFIG_DIR / "suivi.yaml"
PRIX_OUVERTURE_DIR = ROOT / "data" / "prix-ouverture"

PARIS_TZ = ZoneInfo("Europe/Paris")

# Valeurs de repli si la config est absente/illisible (la mesure ne doit jamais
# planter pour une config manquante — mais la config est la source de vérité).
_DEFAULT_MARKET_HOURS: Dict[str, Dict[str, str]] = {
    "eu": {"open": "09:00", "close": "17:30"},
    "us": {"open": "15:30", "close": "22:00"},
    "continu": {"open": "08:00", "close": "22:00"},
}
_DEFAULT_OPEN_STAMP_DELAY_MIN = 5
_DEFAULT_NEUTRAL_BAND_PCT = 0.001
# Mapping famille de fiche → groupe de marché (cf. suivi.yaml).
# `indices` est ambigu (CAC = eu, S&P/Nasdaq = us) → désambiguïsé par nom via
# les overrides de la config. Tout le reste (fx, métaux, agri, énergie) = continu.
_FAMILY_GROUP: Dict[str, str] = {
    "indices": "us",          # défaut US ; CAC ramené à "eu" par override nom
    "volatilité": "us",
    "fx": "continu",
    "métaux-précieux": "continu",
    "métaux-industriels": "continu",
    "agri": "continu",
    "agri-softs": "continu",
    "énergie": "continu",
}

# Proxies Twelve Data pour les indices US « ^ » (fetch du stamp uniquement).
# Diagnostic 03/07 : ^GSPC / ^IXIC / ^VIX sont blacklistés côté Twelve (indices ^
# → fallback yfinance, bloqué en CI) → le fetch rendait None et le stamp restait
# vide même quand il tournait. Or TOUT le système cote déjà ces actifs à l'échelle
# ETF/proxy (bulletin : Nasdaq 735.8 = échelle QQQ) et SPY/QQQ/VIXY sont prouvés
# vivants sur Twelve en CI. On mappe donc le TICKER DE FETCH vers son proxy, mais on
# STOCKE le prix sous la clé ticker_principal habituelle → cohérent avec les prix
# d'émission déjà en échelle proxy. Zéro invention : simple substitution de source.
STAMP_INDEX_PROXY: Dict[str, str] = {
    "^GSPC": "SPY",
    "^IXIC": "QQQ",
    "^VIX": "VIXY",
}

# Tolérance d'égalité (proportion) sous laquelle deux prix d'ouverture sont
# considérés identiques (jitter d'arrondi). Au-delà, une tentative d'écrasement
# est loggée comme violation de l'entry-lock. Aligné avec journaliste.py.
ENTRY_LOCK_PRICE_EPS = 1e-9


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_suivi_config(path: Path = SUIVI_CONFIG_FILE) -> dict:
    """Charge v3/config/suivi.yaml. Repli sur défauts si absent/illisible."""
    if not path.exists():
        logger.warning("suivi.yaml absent (%s) — défauts utilisés", path)
        return {}
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except Exception as e:  # noqa: BLE001
        logger.warning("suivi.yaml illisible (%s) : %s — défauts utilisés", path, e)
        return {}
    return data if isinstance(data, dict) else {}


def market_hours(config: Optional[dict] = None) -> Dict[str, Dict[str, str]]:
    config = config if config is not None else load_suivi_config()
    mh = config.get("market_hours")
    if isinstance(mh, dict) and mh:
        return mh
    return _DEFAULT_MARKET_HOURS


def open_stamp_delay_min(config: Optional[dict] = None) -> int:
    config = config if config is not None else load_suivi_config()
    val = config.get("open_stamp_delay_min")
    try:
        return int(val) if val is not None else _DEFAULT_OPEN_STAMP_DELAY_MIN
    except (TypeError, ValueError):
        return _DEFAULT_OPEN_STAMP_DELAY_MIN


def neutral_band_pct(config: Optional[dict] = None) -> float:
    config = config if config is not None else load_suivi_config()
    val = config.get("neutral_band_pct")
    try:
        return float(val) if val is not None else _DEFAULT_NEUTRAL_BAND_PCT
    except (TypeError, ValueError):
        return _DEFAULT_NEUTRAL_BAND_PCT


def _parse_hhmm(s: str) -> time:
    """Parse 'HH:MM' → time. Lève ValueError si invalide (zéro invention)."""
    h, m = s.split(":")
    return time(hour=int(h), minute=int(m))


# ---------------------------------------------------------------------------
# Mapping actif → groupe de marché
# ---------------------------------------------------------------------------

def actif_group(fiche: dict, config: Optional[dict] = None) -> Optional[str]:
    """Groupe de marché (eu / us / continu) d'un actif, depuis sa fiche.

    Résolution déterministe :
      1. Override par nom d'actif (config `group_overrides_by_actif`) — prioritaire,
         désambiguïse les indices (CAC = eu, S&P/Nasdaq = us).
      2. Sinon, mapping par famille (`_FAMILY_GROUP`).
      3. Sinon → None (groupe inconnu : zéro invention, l'appelant skippe).
    """
    config = config if config is not None else load_suivi_config()
    actif_name = (fiche.get("actif") or "").strip()
    overrides = config.get("group_overrides_by_actif") or {}
    if isinstance(overrides, dict) and actif_name in overrides:
        g = overrides[actif_name]
        if g in ("eu", "us", "continu"):
            return g
    famille = (fiche.get("famille") or "").strip()
    return _FAMILY_GROUP.get(famille)


def group_open_time(group: str, config: Optional[dict] = None) -> Optional[time]:
    """Heure d'ouverture Paris du groupe (time), ou None si groupe inconnu."""
    mh = market_hours(config)
    grp = mh.get(group)
    if not isinstance(grp, dict):
        return None
    try:
        return _parse_hhmm(grp["open"])
    except (KeyError, ValueError):
        return None


def group_close_time(group: str, config: Optional[dict] = None) -> Optional[time]:
    """Heure de clôture Paris du groupe (time), ou None si groupe inconnu."""
    mh = market_hours(config)
    grp = mh.get(group)
    if not isinstance(grp, dict):
        return None
    try:
        return _parse_hhmm(grp["close"])
    except (KeyError, ValueError):
        return None


def is_open_for_stamp(
    group: str,
    now: datetime,
    config: Optional[dict] = None,
) -> bool:
    """True si l'heure Paris `now` est >= ouverture du groupe + délai (CA-M2).

    `now` est converti en Europe/Paris (DST géré par ZoneInfo, jamais d'offset
    en dur). Un `now` naïf est supposé déjà en heure de Paris. Le marché du
    groupe doit être ouvert depuis au moins OPEN_STAMP_DELAY_MIN minutes pour
    que son prix d'ouverture soit stampable.
    """
    open_t = group_open_time(group, config)
    if open_t is None:
        return False
    now_paris = _to_paris(now)
    delay = open_stamp_delay_min(config)
    # Heure d'ouverture stampable = ouverture + délai, le même jour.
    open_dt = datetime.combine(now_paris.date(), open_t, tzinfo=PARIS_TZ)
    open_plus = open_dt.timestamp() + delay * 60
    return now_paris.timestamp() >= open_plus


def _to_paris(now: datetime) -> datetime:
    """Convertit `now` en Europe/Paris. Naïf → supposé déjà Paris (localisé)."""
    if now.tzinfo is None:
        return now.replace(tzinfo=PARIS_TZ)
    return now.astimezone(PARIS_TZ)


# ---------------------------------------------------------------------------
# Prix d'ouverture : I/O
# ---------------------------------------------------------------------------

def prix_ouverture_path(
    date_j: date, base_dir: Path = PRIX_OUVERTURE_DIR
) -> Path:
    """Chemin du fichier prix-ouverture du jour (1 fichier/jour, clé par date)."""
    return base_dir / f"{date_j.isoformat()}.json"


def load_prix_ouverture(
    date_j: date, base_dir: Path = PRIX_OUVERTURE_DIR
) -> Dict[str, float]:
    """Lit `prix-ouverture/{date_j}.json` → {ticker: prix}. {} si absent."""
    p = prix_ouverture_path(date_j, base_dir)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("prix-ouverture illisible %s : %s", p, e)
        return {}
    if not isinstance(data, dict):
        return {}
    out: Dict[str, float] = {}
    for k, v in data.items():
        try:
            out[str(k)] = float(v)
        except (TypeError, ValueError):
            continue
    return out


def _enforce_entry_lock_ouverture(
    existing: Dict[str, float],
    ticker: str,
    proposed_price: float,
    date_j: date,
) -> float:
    """Immutabilité du prix d'ouverture (même logique que prix d'émission).

    Si `ticker` déjà stampé pour ce jour → on garde l'ancien (jamais écrasé).
    Log WARNING si l'écart dépasse ENTRY_LOCK_PRICE_EPS (tentative d'écrasement).
    Pure (lecture seule).
    """
    locked = existing.get(ticker)
    if locked is None:
        return proposed_price
    try:
        diff = abs(float(proposed_price) - float(locked))
        rel = diff / abs(locked) if locked != 0 else diff
    except (TypeError, ValueError):
        rel = float("nan")
    if rel > ENTRY_LOCK_PRICE_EPS:
        logger.warning(
            "entry-lock ouverture violé (ignoré) : %s @ %s ancien=%s proposé=%s "
            "(diff rel=%.3e) — prix d'ouverture immuable, ancien préservé",
            ticker, date_j.isoformat(), locked, proposed_price, rel,
        )
    return locked


# ---------------------------------------------------------------------------
# Stamp prix d'ouverture
# ---------------------------------------------------------------------------

def stamp_prix_ouverture(
    date_j: Optional[date] = None,
    fiches: Optional[Dict[str, dict]] = None,
    fetch_price: Optional[Any] = None,
    base_dir: Path = PRIX_OUVERTURE_DIR,
    now: Optional[datetime] = None,
    config: Optional[dict] = None,
) -> Path:
    """Stampe le prix d'ouverture du jour pour chaque actif dont le marché est ouvert.

    Comportement (spec §2.5) :
    1. Pour chaque actif, résoudre son groupe → heure d'ouverture.
    2. Stamper UNIQUEMENT si l'heure Paris `now` >= ouverture + OPEN_STAMP_DELAY_MIN
       (CA-M2 : un prix récupéré avant ce délai est rejeté — pas stampé).
    3. fetch_price(ticker) → prix spot. None → ticker ABSENT du JSON (CA-M3,
       zéro invention) → Journaliste : suivi-interrompu, retry au run suivant.
    4. Idempotent + entry-lock par actif : un ticker déjà stampé ce jour n'est
       PAS refetché ni écrasé (CA-M1).

    Args :
        date_j : jour de stamp (défaut = aujourd'hui Paris).
        now : datetime de référence (défaut = maintenant Paris). Injecté en test.
        fetch_price : callable(ticker)->Optional[float]. Défaut : Twelve Data.
        config : config suivi.yaml préchargée (sinon rechargée).

    Returns : chemin du fichier prix-ouverture/{date_j}.json écrit.
    """
    now = now or datetime.now(PARIS_TZ)
    now = _to_paris(now)
    date_j = date_j or now.date()
    config = config if config is not None else load_suivi_config()
    if fiches is None:
        # Lazy import pour ne pas dépendre du module mesure dans tous les contextes.
        import journaliste  # noqa: PLC0415
        fiches = journaliste.load_fiches()
    if fetch_price is None:
        import criteres_calculator  # noqa: PLC0415
        fetch_price = criteres_calculator.fetch_twelve_price

    base_dir.mkdir(parents=True, exist_ok=True)
    out_path = prix_ouverture_path(date_j, base_dir)
    existing = load_prix_ouverture(date_j, base_dir)
    stamped: Dict[str, float] = dict(existing)

    for fiche_key, fiche in fiches.items():
        ticker = fiche.get("ticker_principal")
        if not ticker:
            continue
        if ticker in existing:
            # Déjà stampé ce jour : idempotence + entry-lock, on ne refetch pas.
            continue
        group = actif_group(fiche, config)
        if group is None:
            logger.warning(
                "stamp ouverture %s : groupe de marché inconnu (famille=%r) — skip",
                ticker, fiche.get("famille"),
            )
            continue
        if not is_open_for_stamp(group, now, config):
            # Marché pas encore ouvert (+ délai) → on n'invente pas un prix.
            # Sera stampé à un run ultérieur (12h/18h/22h).
            logger.info(
                "stamp ouverture %s : marché %s pas encore ouvert à %s Paris — retry plus tard",
                ticker, group, now.strftime("%H:%M"),
            )
            continue
        # Indices US « ^ » blacklistés Twelve → fetch via proxy ETF (SPY/QQQ/VIXY),
        # mais on conserve la clé `ticker` d'origine pour le stockage (échelle proxy
        # cohérente avec les prix d'émission).
        fetch_ticker = STAMP_INDEX_PROXY.get(ticker, ticker)
        try:
            price = fetch_price(fetch_ticker)
        except Exception as e:  # noqa: BLE001
            logger.warning("stamp ouverture %s : exception %s", ticker, e)
            price = None
        if price is None:
            logger.warning(
                "stamp ouverture %s : indisponible (Twelve KO) — absent du JSON (suivi-interrompu)",
                ticker,
            )
            continue
        try:
            new_price = float(price)
        except (TypeError, ValueError):
            continue
        stamped[ticker] = _enforce_entry_lock_ouverture(
            existing, ticker, new_price, date_j,
        )

    out_path.write_text(
        json.dumps(stamped, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    logger.info(
        "Prix d'ouverture stampés %s : %d tickers (à %s Paris)",
        out_path, len(stamped), now.strftime("%H:%M"),
    )
    return out_path


__all__ = [
    "PRIX_OUVERTURE_DIR",
    "PARIS_TZ",
    "load_suivi_config",
    "market_hours",
    "open_stamp_delay_min",
    "neutral_band_pct",
    "actif_group",
    "group_open_time",
    "group_close_time",
    "is_open_for_stamp",
    "prix_ouverture_path",
    "load_prix_ouverture",
    "stamp_prix_ouverture",
]
