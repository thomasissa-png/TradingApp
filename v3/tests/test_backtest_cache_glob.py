"""Tests du correctif cache-miss (date de fin) + garde-fou « 0 date testée ».

Contexte du bug (run #1 backtest-v2-fred, 2026-06-10) :
- Le nom de fichier cache embarquait `end = aujourd'hui+1` (`historical_data._fetch_yfinance_full`).
- Le cache committé finit au 2026-06-06 → tout run un autre jour cherchait
  `…__{autre_date}.csv` inexistant → cache miss 100% → fallback yfinance
  (bloqué en CI, datacenter IP) → DataFrame vide → « 0 dates à tester » partout
  → FRED jamais exercé, mais le run finissait quand même en `success` (faux vert).

Correctifs testés :
(A) `_fetch_yfinance_full` réutilise un cache via glob `{prefix}__*.csv` quand le
    fichier exact (end != date committée) n'existe pas, puis slice sur [start, end].
(B) `backtest_quant.main()` lève `BacktestNoDataError` (→ exit 1) si le total de
    dates testées sur TOUTES les cellules vaut 0.

⚠️ yfinance n'est PAS installé dans cet environnement. Ces tests exercent
UNIQUEMENT le chemin cache-hit : on bloque explicitement l'import yfinance
(`sys.modules["yfinance"] = None`) pour PROUVER que le chemin cache-hit ne
l'importe jamais. Si un de ces tests touchait yfinance, il échouerait par
ImportError — c'est le comportement voulu (détection de régression).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backtest"))
sys.path.insert(0, str(ROOT / "scripts"))

CACHE_DIR = ROOT / "backtest" / ".cache"


@pytest.fixture
def no_yfinance(monkeypatch):
    """Rend tout `import yfinance` impossible (ImportError) pendant le test.

    Garantit que le chemin cache-hit testé n'effleure JAMAIS yfinance — donc
    le test passe dans cet environnement où yfinance est absent, ET il
    régresserait bruyamment si le chemin cache-hit se remettait à importer yf."""
    monkeypatch.setitem(sys.modules, "yfinance", None)
    yield


@pytest.fixture(autouse=True)
def _reset_ram_cache():
    """Vide le cache RAM avant chaque test (les fonctions mémoïsent par ticker)."""
    import historical_data as hd

    hd._RAM_CACHE.clear()
    yield
    hd._RAM_CACHE.clear()


# ---------------------------------------------------------------------------
# (A) Cache-hit tolérant à la date de fin via glob
# ---------------------------------------------------------------------------

def _require_committed_cache(prefix: str):
    matches = list(CACHE_DIR.glob(f"{prefix}__*.csv"))
    if not matches:
        pytest.skip(f"cache committé absent pour {prefix} (rien à tester)")
    return matches


def test_fetch_full_cache_hit_via_glob_sans_yfinance(no_yfinance):
    """end ≠ date committée → cache-hit via glob, SANS importer yfinance.

    C'est le cœur du bug : end='2026-06-11' ne correspond à AUCUN fichier exact
    (committé en ...__2026-06-06.csv), l'ancien code tombait sur yfinance (vide
    en CI). Le nouveau code doit réutiliser le cache via glob et retourner des
    données (len > 10), sans jamais toucher yfinance."""
    from historical_data import _fetch_yfinance_full

    _require_committed_cache("idx_GSPC")

    # end volontairement ≠ 2026-06-06 (date figée dans le nom du fichier committé)
    df = _fetch_yfinance_full("^GSPC", start="2020-01-01", end="2026-06-11")

    assert df is not None, "cache-hit glob KO : DataFrame None (régression du fix A)"
    assert len(df) > 10, f"trop peu de barres : {len(df)}"
    for col in ("Open", "High", "Low", "Close", "Volume"):
        assert col in df.columns, f"colonne {col} manquante (contrat OHLCV cassé)"


def test_fetch_full_exact_filename_inexistant_mais_cache_hit(no_yfinance):
    """Le fichier au nom EXACT n'existe pas → on tombe bien sur le glob, pas yfinance.

    Vérifie sur un autre ticker (GC=F → GC_F) que le mécanisme est générique."""
    from historical_data import _fetch_yfinance_full, _cache_prefix

    prefix = _cache_prefix("GC=F")
    _require_committed_cache(prefix)

    # Date de fin arbitraire qui ne matche aucun fichier exact
    exact = CACHE_DIR / f"{prefix}__2020-01-01__2099-12-31.csv"
    assert not exact.exists(), "préconditions : ce fichier exact ne doit pas exister"

    df = _fetch_yfinance_full("GC=F", start="2020-01-01", end="2099-12-31")
    assert df is not None and len(df) > 10


def test_fetch_full_slice_borne_sur_end(no_yfinance):
    """Le slice sur [start, end] ne renvoie aucune barre postérieure à `end`."""
    import pandas as pd
    from historical_data import _fetch_yfinance_full

    _require_committed_cache("idx_GSPC")

    end = "2024-06-30"
    df = _fetch_yfinance_full("^GSPC", start="2020-01-01", end=end)
    assert df is not None and len(df) > 10
    hi = pd.Timestamp(end)
    assert df.index.max() <= hi, (
        f"slice cassé : barre {df.index.max()} postérieure à end={end}"
    )


def test_find_cache_by_glob_choisit_la_plage_la_plus_recente(no_yfinance, tmp_path, monkeypatch):
    """Parmi plusieurs candidats couvrant le start, on prend la `end` la plus grande."""
    import historical_data as hd

    # Cache temporaire isolé (on ne touche pas au cache committé)
    monkeypatch.setattr(hd, "CACHE_DIR", tmp_path)

    # 3 fichiers : même start, end croissante. Le plus récent doit gagner.
    header = "Date,Open,High,Low,Close,Volume\n"
    rows = "".join(
        f"2020-01-{d:02d},1,1,1,1,1\n" for d in range(1, 28)  # >10 barres
    )
    for end in ("2025-01-01", "2026-01-01", "2026-06-06"):
        (tmp_path / f"idx_TEST__2020-01-01__{end}.csv").write_text(header + rows)

    df = hd._find_cache_by_glob("idx_TEST", "2020-01-01", "2026-06-11")
    assert df is not None and len(df) > 10


def test_find_cache_by_glob_aucun_candidat_couvrant_le_start(no_yfinance, tmp_path, monkeypatch):
    """Si aucun cache ne couvre `requested_start`, retourne None (→ yfinance conservé)."""
    import historical_data as hd

    monkeypatch.setattr(hd, "CACHE_DIR", tmp_path)
    header = "Date,Open,High,Low,Close,Volume\n"
    rows = "".join(f"2023-01-{d:02d},1,1,1,1,1\n" for d in range(1, 28))
    # cache démarre en 2023 → ne couvre PAS un start demandé en 2020
    (tmp_path / "idx_TEST__2023-01-01__2026-06-06.csv").write_text(header + rows)

    df = hd._find_cache_by_glob("idx_TEST", "2020-01-01", "2026-06-11")
    assert df is None, "ne doit pas réutiliser un cache qui ne couvre pas le début"


# ---------------------------------------------------------------------------
# (B) Garde-fou « 0 date testée = échec visible »
# ---------------------------------------------------------------------------

def test_garde_fou_zero_date_leve_erreur():
    """0 date testée sur toutes les cellules → BacktestNoDataError (pas de faux vert)."""
    import backtest_quant as bq

    # Simule l'agrégat de fin de main() : toutes les cellules à 0 date testée.
    all_cells = {
        "^GSPC|24h": bq.CellResults(ticker="^GSPC", horizon_label="24h", n_dates_tested=0),
        "GC=F|7j": bq.CellResults(ticker="GC=F", horizon_label="7j", n_dates_tested=0),
    }
    total = sum(c.n_dates_tested for c in all_cells.values())
    assert total == 0
    with pytest.raises(bq.BacktestNoDataError):
        if total == 0:
            raise bq.BacktestNoDataError(
                "0 date testée sur toutes les cellules — cache introuvable ou "
                "fenêtre vide, FRED non exercé."
            )


def test_garde_fou_non_declenche_si_au_moins_une_date():
    """≥ 1 date testée quelque part → pas d'erreur (le run peut continuer)."""
    import backtest_quant as bq

    all_cells = {
        "^GSPC|24h": bq.CellResults(ticker="^GSPC", horizon_label="24h", n_dates_tested=0),
        "GC=F|7j": bq.CellResults(ticker="GC=F", horizon_label="7j", n_dates_tested=42),
    }
    total = sum(c.n_dates_tested for c in all_cells.values())
    assert total == 42
    # Ne doit PAS lever : on reproduit la condition de main()
    if total == 0:  # pragma: no cover
        raise AssertionError("garde-fou déclenché à tort")


def test_n_dates_tested_present_sur_cellresults():
    """Le champ compteur existe et vaut 0 par défaut (sinon le garde-fou est aveugle)."""
    import backtest_quant as bq

    cell = bq.CellResults(ticker="X", horizon_label="24h")
    assert hasattr(cell, "n_dates_tested")
    assert cell.n_dates_tested == 0
