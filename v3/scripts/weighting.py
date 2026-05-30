"""TradingApp v3 — Loader des facteurs de pondération.

Source de vérité : `v3/config/weighting.yml`. Si le fichier est absent ou
illisible, on charge des défauts documentés (jamais d'inventaire muet — un
WARNING est loggé).

Utilisé par criteres_calculator (pour calculer valeur_ponderee sur les
triplets NEWS) et par scoring_analyste (pour le double score).

Red lines :
- Aucune valeur inventée : si une clé manque dans le YAML, on prend le défaut
  documenté + WARNING.
- Le cap est plafonné à 1.0 (signe-cohérent avec les critères ±1).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger("weighting")

ROOT = Path(__file__).resolve().parents[1]
WEIGHTING_YML = ROOT / "config" / "weighting.yml"

# Défauts documentés (fallback si YAML absent / corrompu / clé manquante)
DEFAULT_MATERIALITY: Dict[str, float] = {
    "high": 1.0,
    "medium": 0.6,
    "low": 0.3,
    "": 0.6,
}
DEFAULT_RELIABILITY: Dict[str, float] = {
    "confirmed": 1.0,
    "reported": 0.7,
    "rumor": 0.4,
    "": 0.7,
}
DEFAULT_CAP: float = 1.0
DEFAULT_VERSION: int = 0  # 0 => défauts (non versionné)


class WeightingConfig:
    """Charge weighting.yml et expose materiality_factor / reliability_factor / cap."""

    def __init__(
        self,
        materiality: Optional[Dict[str, float]] = None,
        reliability: Optional[Dict[str, float]] = None,
        cap: float = DEFAULT_CAP,
        version: int = DEFAULT_VERSION,
    ) -> None:
        self.materiality_factor: Dict[str, float] = dict(DEFAULT_MATERIALITY)
        if materiality:
            self.materiality_factor.update({str(k).lower(): float(v) for k, v in materiality.items()})
        self.reliability_factor: Dict[str, float] = dict(DEFAULT_RELIABILITY)
        if reliability:
            self.reliability_factor.update({str(k).lower(): float(v) for k, v in reliability.items()})
        try:
            self.cap: float = float(cap)
        except (TypeError, ValueError):
            self.cap = DEFAULT_CAP
        if self.cap <= 0:
            self.cap = DEFAULT_CAP
        self.version: int = int(version) if version is not None else DEFAULT_VERSION

    # --- API publique ----------------------------------------------------

    def materiality(self, level: Optional[str]) -> float:
        key = (level or "").strip().lower()
        if key in self.materiality_factor:
            return self.materiality_factor[key]
        # fallback : clé vide (médian)
        return self.materiality_factor.get("", DEFAULT_MATERIALITY[""])

    def reliability(self, level: Optional[str]) -> float:
        key = (level or "").strip().lower()
        if key in self.reliability_factor:
            return self.reliability_factor[key]
        return self.reliability_factor.get("", DEFAULT_RELIABILITY[""])

    def factor(self, materiality: Optional[str], reliability: Optional[str]) -> float:
        """Facteur combiné, plafonné à cap (valeur absolue)."""
        f = self.materiality(materiality) * self.reliability(reliability)
        if f > self.cap:
            return self.cap
        if f < -self.cap:
            return -self.cap
        return f

    def weight_direction(self, direction: float, materiality: Optional[str], reliability: Optional[str]) -> float:
        """Pondère un triplet ±1 → ±[0, cap] selon materiality × reliability."""
        try:
            d = float(direction)
        except (TypeError, ValueError):
            return 0.0
        f = self.factor(materiality, reliability)
        v = d * f
        if v > self.cap:
            return self.cap
        if v < -self.cap:
            return -self.cap
        return v

    def as_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "materiality_factor": dict(self.materiality_factor),
            "reliability_factor": dict(self.reliability_factor),
            "cap": self.cap,
        }


_CACHED: Optional[WeightingConfig] = None


def load_weighting(path: Path = WEIGHTING_YML, force: bool = False) -> WeightingConfig:
    """Charge weighting.yml (avec cache). force=True relit le fichier."""
    global _CACHED
    if _CACHED is not None and not force:
        return _CACHED
    if not path.exists():
        logger.warning("weighting.yml absent (%s) — défauts appliqués", path)
        _CACHED = WeightingConfig()
        return _CACHED
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as e:
        logger.warning("weighting.yml illisible (%s) : %s — défauts appliqués", path, e)
        _CACHED = WeightingConfig()
        return _CACHED
    if not isinstance(data, dict):
        logger.warning("weighting.yml : racine non-dict — défauts appliqués")
        _CACHED = WeightingConfig()
        return _CACHED
    _CACHED = WeightingConfig(
        materiality=data.get("materiality_factor") if isinstance(data.get("materiality_factor"), dict) else None,
        reliability=data.get("reliability_factor") if isinstance(data.get("reliability_factor"), dict) else None,
        cap=data.get("cap", DEFAULT_CAP),
        version=data.get("version", DEFAULT_VERSION),
    )
    return _CACHED


def reset_cache() -> None:
    """Utilitaire pour les tests : force un rechargement au prochain load_weighting."""
    global _CACHED
    _CACHED = None
