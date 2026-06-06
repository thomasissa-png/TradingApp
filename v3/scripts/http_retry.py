"""TradingApp v3 — Helper HTTP générique résilient (retry backoff + throttle).

Factorise la logique de résilience initialement développée pour FRED
(`criteres_calculator._fred_get_json`) afin de la rendre réutilisable par les
fetchers news (RSS, GNews, NewsAPI) qui subissent le MÊME 429 Too Many Requests.

Garanties :
- Retry exponentiel (base 2s → 4s → 8s + jitter) UNIQUEMENT sur 429 et 5xx,
  en respectant l'en-tête `Retry-After` s'il est présent.
- Throttle minimal entre requêtes d'un même bucket (anti-rafale, env-configurable).
- Statuts non-retriables (4xx ≠ 429, ex : 403, 404) → AUCUN retry (le retry
  n'aide pas sur un blocage d'accès ou une ressource absente) → échec immédiat.
- Zéro régression sur 200 : succès au 1er essai = comportement strictement
  identique à un `requests.get` direct (retourne la Response telle quelle).
- Le caller gère lui-même le parsing (.content pour feedparser, .json() pour les
  APIs) ET l'incrément de son compteur d'échec / source_monitor : ce helper ne
  fait que renvoyer la Response (succès) ou None (échec après épuisement /
  statut non-retriable / erreur réseau).

Conçu pour être mockable en tests : import paresseux de `requests` à l'intérieur.
"""

from __future__ import annotations

import logging
import os
import random
import threading
import time
from typing import Any, Dict, Optional

logger = logging.getLogger("http_retry")

# Statuts qui justifient un retry (rate-limit + erreurs serveur transitoires).
# 403/404/401 NE sont PAS ici : retry inutile sur un blocage d'accès stable.
RETRY_STATUS = frozenset({429, 500, 502, 503, 504})

# Set étendu pour les flux protégés par un WAF (ex Cloudflare) qui renvoie un
# 403 INTERMITTENT (challenge transitoire selon l'IP/géo de l'appelant) plutôt
# qu'un refus permanent. Sur ces flux précis (RSS scrapables), un 403 est parfois
# récupérable au retry suivant — contrairement à un 403 d'API (clé invalide). À
# n'utiliser QUE via le paramètre retry_status d'un appel ciblé, jamais en défaut
# global (FRED/GNews/NewsAPI gardent RETRY_STATUS).
# NB (06/06) : ce retry ne sauve PAS un 403 PERMANENT par plage d'IP — c'est ce
# qui a fait retirer mining_com (Cloudflare bloquait toutes les IP runner GitHub,
# le retry ne pouvait rien y faire). Le mécanisme reste utile aux autres RSS.
RETRY_STATUS_WITH_403 = frozenset({403, 429, 500, 502, 503, 504})

# Paramètres par défaut (env-configurables). Le préfixe HTTP_RETRY_* évite toute
# collision avec les variables FRED_* déjà en place.
DEFAULT_MAX_RETRIES = int(os.environ.get("HTTP_RETRY_MAX_RETRIES", "3"))
DEFAULT_BACKOFF_BASE = float(os.environ.get("HTTP_RETRY_BACKOFF_BASE", "2.0"))  # 2s → 4s → 8s
DEFAULT_MIN_INTERVAL = float(os.environ.get("HTTP_RETRY_MIN_INTERVAL", "0.5"))  # throttle inter-requêtes
DEFAULT_TIMEOUT = int(os.environ.get("HTTP_RETRY_TIMEOUT", "15"))

# Throttle par bucket : chaque source (rss/gnews/newsapi/fred...) a son propre
# espace de cadence pour ne pas se pénaliser mutuellement.
_throttle_lock = threading.Lock()
_last_request_ts: Dict[str, float] = {}


def parse_retry_after(value: Optional[str]) -> Optional[float]:
    """Parse l'en-tête Retry-After (secondes uniquement ; date HTTP ignorée).

    Retourne None si absent / illisible / format date → le caller retombe sur le
    backoff exponentiel.
    """
    if not value:
        return None
    try:
        secs = float(str(value).strip())
    except (TypeError, ValueError):
        return None  # format date HTTP non géré → backoff
    return secs if secs >= 0 else None


def backoff_delay(attempt: int, retry_after: Optional[float],
                  *, backoff_base: float = DEFAULT_BACKOFF_BASE) -> float:
    """Délai avant retry : Retry-After (si fourni) sinon backoff exponentiel + jitter.

    `attempt` est 1-indexé (1 = premier essai). Le jitter (0..0.5s) évite le
    thundering herd quand plusieurs sources retryent en même temps.
    """
    if retry_after is not None and retry_after >= 0:
        return retry_after + random.uniform(0, 0.5)
    base = backoff_base * (2 ** (attempt - 1))  # 2, 4, 8...
    return base + random.uniform(0, 0.5)


def _throttle(bucket: str, min_interval: float) -> None:
    """Espacement minimal entre deux requêtes du même bucket (anti-rafale).

    Bloque (sleep) le temps nécessaire pour respecter `min_interval` depuis la
    dernière requête de ce bucket. Thread-safe ; le sleep est fait sous lock (les
    fetchers news sont séquentiels dans un run, pas de contention notable).
    """
    if min_interval <= 0:
        return
    with _throttle_lock:
        now = time.monotonic()
        last = _last_request_ts.get(bucket, 0.0)
        wait = min_interval - (now - last)
        if wait > 0:
            time.sleep(wait)
        _last_request_ts[bucket] = time.monotonic()


def http_get_retry(
    url: str,
    *,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: int = DEFAULT_TIMEOUT,
    bucket: str = "default",
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_base: float = DEFAULT_BACKOFF_BASE,
    min_interval: float = DEFAULT_MIN_INTERVAL,
    label: str = "",
    status_out: Optional[Dict[str, Any]] = None,
    retry_status: Optional[frozenset] = None,
) -> Optional[Any]:
    """GET résilient : throttle + retry backoff sur 429/5xx, retourne la Response.

    Args:
        url, params, headers, timeout : passés tels quels à requests.get.
        bucket : espace de throttle (ex "rss", "gnews", "newsapi"). Sources
            distinctes = cadences indépendantes.
        max_retries : nombre TOTAL de tentatives (>= 1).
        backoff_base : base du backoff exponentiel (2.0 → 2s/4s/8s).
        min_interval : espacement minimal entre requêtes du même bucket (s).
        label : libellé pour les logs (nom de la source).
        status_out : dict optionnel mis à jour par le helper pour exposer au
            caller le dernier statut HTTP observé (clé "status", str) et l'erreur
            réseau éventuelle (clé "error"). Permet au monitoring de garder la
            visibilité du code (ex 403/404/429) même quand le helper renvoie None.
        retry_status : set de statuts HTTP à retenter (défaut RETRY_STATUS =
            {429,5xx}). Passer RETRY_STATUS_WITH_403 pour les flux RSS derrière un
            WAF qui renvoie des 403 intermittents. N'élargit le retry QUE pour cet
            appel — pas de changement global.

    Returns:
        La `requests.Response` en cas de succès HTTP < 400.
        None si : requests indisponible, erreur réseau persistante, statut
        non-retriable (4xx ≠ 429, ex 403/404), ou épuisement des retries sur
        429/5xx. Le caller décide alors quoi faire (record_call ko, etc.).

    Note : ne lève JAMAIS (sauf bug interne) — l'objectif est que le caller
    branche son échec/monitoring sur un None, pas sur une exception.
    """
    try:
        import requests  # lazy import (mockable / optionnel)
    except ImportError:
        logger.warning("requests non installé — HTTP désactivé (%s)", label or url)
        return None

    tag = label or url
    last_err: Optional[str] = None
    retriable = retry_status if retry_status is not None else RETRY_STATUS

    for attempt in range(1, max_retries + 1):
        _throttle(bucket, min_interval)
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        except Exception as e:  # noqa: BLE001 — erreur réseau / timeout
            last_err = str(e)
            if status_out is not None:
                status_out["status"] = "net_error"
                status_out["error"] = str(e)
            logger.warning(
                "HTTP %s : erreur réseau (tentative %d/%d) : %s",
                tag, attempt, max_retries, e,
            )
            if attempt < max_retries:
                time.sleep(backoff_delay(attempt, None, backoff_base=backoff_base))
            continue

        status = resp.status_code
        if status_out is not None:
            status_out["status"] = str(status)

        # Succès : on rend la Response telle quelle (le caller parse).
        if status < 400:
            return resp

        # Statut retriable (429/5xx, +403 si retry_status l'inclut) ET il reste
        # des tentatives → backoff.
        if status in retriable and attempt < max_retries:
            retry_after = parse_retry_after(resp.headers.get("Retry-After"))
            delay = backoff_delay(attempt, retry_after, backoff_base=backoff_base)
            logger.warning(
                "HTTP %s : statut %d (tentative %d/%d) → retry dans %.1fs",
                tag, status, attempt, max_retries, delay,
            )
            time.sleep(delay)
            last_err = f"HTTP {status}"
            continue

        # Statut non-retriable (4xx hors `retriable`, ex 404, ou 403 quand
        # retry_status ne l'inclut pas) OU dernière tentative épuisée sur un
        # statut retriable → échec sans nouveau retry.
        last_err = f"HTTP {status}"
        break

    logger.warning(
        "HTTP %s : échec après %d tentative(s) — %s",
        tag, max_retries, last_err or "raison inconnue",
    )
    return None
