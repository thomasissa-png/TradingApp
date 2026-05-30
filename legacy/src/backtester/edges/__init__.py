"""Edges Wave 1 — H-C ORB et H-A Gap Follow.

Source de vérité : docs/analytics/edge-rnd-report.md §3.

Wave 2 (H-B/H-D/H-E/H-F/H-G) sera lancée seulement si ≥ 1 edge de wave 1
PASS les 6 conditions AND v1.1.
"""

from __future__ import annotations

from typing import Protocol

import pandas as pd


class EdgeStrategy(Protocol):
    """Interface commune des stratégies d'edge.

    Chaque edge implémente generate_signals(df, params) qui retourne un
    DataFrame de signaux exploitables par le runner.
    """

    edge_id: str

    def generate_signals(
        self,
        df: pd.DataFrame,
        params: dict[str, float | int],
    ) -> pd.DataFrame:
        """Génère les signaux pour la période fournie.

        Args:
            df : OHLC 1min indexé par DatetimeIndex UTC, colonnes
                 [open, high, low, close, volume].
            params : paramètres de l'edge (varient selon implémentation).

        Returns:
            DataFrame avec colonnes :
            - timestamp (DatetimeIndex)
            - direction (str : 'BUY', 'SELL', 'NONE')
            - entry (float, NaN si NONE)
            - sl (float, NaN si NONE)
            - tp (float, NaN si NONE)
            - raison (str, justification courte du signal)
        """
        ...


from src.backtester.edges.h_a_gap_follow import H_A_GapFollow  # noqa: E402
from src.backtester.edges.h_c_orb import H_C_ORB  # noqa: E402

__all__ = ["H_C_ORB", "EdgeStrategy", "H_A_GapFollow"]
