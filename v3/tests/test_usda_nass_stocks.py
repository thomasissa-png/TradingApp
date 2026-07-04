"""Fix 03/07 — handler USDA NASS QuickStats pour les stocks trimestriels de blé
(cle usda_wasde_stocks_to_use, poids 11). Tests 100% MOCKÉS (zéro réseau) :
`http_get_json` est monkeypatché avec un JSON NASS réaliste.

Écart assumé documenté dans le code : source NASS TRIMESTRIELLE (niveau de stocks)
proxy du ratio stocks/conso WASDE mensuel. Signe -1 appliqué en aval par le scoring
(non testé ici) : le handler émet le z-score brut, comme _handle_eia.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import criteres_calculator as cc  # noqa: E402

TS = "2026-06-10T14:00:00+00:00"


def _row(value, year, period):
    return {"Value": value, "year": year, "reference_period_desc": period,
            "commodity_desc": "WHEAT", "statisticcat_desc": "STOCKS"}


def _nass_payload(rows):
    return {"data": rows}


def _crit():
    return {"cle_courante": "usda_wasde_stocks_to_use", "normalisation": "zscore",
            "source": "USDA WASDE (mensuel)", "zscore_window": 12, "zscore_div": 2,
            "cap": 1.0, "signe": -1}


@pytest.fixture(autouse=True)
def _key(monkeypatch):
    monkeypatch.setenv("USDA_API_KEY", "test-key-1234")
    cc.SKIP_COUNTER.clear()


def test_parse_value_virgules_et_espaces():
    """Séparateurs de milliers virgule ET espace tolérés (attention virgules)."""
    assert cc._parse_nass_value("1,234,567") == 1234567.0
    assert cc._parse_nass_value("1 234 567") == 1234567.0
    assert cc._parse_nass_value("980") == 980.0
    # Codes de suppression / vides → None (n/a propre, pas 0).
    assert cc._parse_nass_value("(D)") is None
    assert cc._parse_nass_value("") is None
    assert cc._parse_nass_value(None) is None


def test_handler_zscore_stocks_trimestriels(monkeypatch):
    """Série trimestrielle croissante → dernier point au-dessus de la moyenne →
    z-score normalisé POSITIF (stocks hauts). Le signe -1 (baissier) est appliqué
    en aval, PAS ici : le handler émet la normalisée brute + la valeur brute."""
    rows = []
    # 8 trimestres autour de ~1000, dernier à 1300 (stocks hauts).
    quarters = [("FIRST OF MAR", 2024, 950), ("FIRST OF JUN", 2024, 980),
                ("FIRST OF SEP", 2024, 1000), ("FIRST OF DEC", 2024, 1010),
                ("FIRST OF MAR", 2025, 990), ("FIRST OF JUN", 2025, 1005),
                ("FIRST OF SEP", 2025, 1020), ("FIRST OF DEC", 2025, 1300)]
    for period, year, val in quarters:
        rows.append(_row(f"{val:,}", year, period))
    monkeypatch.setattr(cc, "http_get_json", lambda *a, **k: _nass_payload(rows))
    out = cc.build_critere_value("ble", _crit(), {}, {},
                                 [], _now())
    assert out is not None
    assert out["valeur"] == 1300.0           # dernier point brut
    assert out["valeur_normalisee"] > 0.0    # au-dessus de la moyenne (stocks hauts)


def test_handler_ordre_chronologique_desordre_entree(monkeypatch):
    """Les lignes NASS arrivent en désordre (tri desc côté API) : le handler
    reconstruit l'ordre chronologique (year, mois) → le « dernier » est bien
    First of Dec 2025, pas la 1re ligne du payload."""
    rows = [
        _row("1,300", 2025, "FIRST OF DEC"),   # le plus récent, listé en 1er
        _row("950", 2024, "FIRST OF MAR"),
        _row("1,020", 2025, "FIRST OF SEP"),
        _row("980", 2024, "FIRST OF JUN"),
        _row("1,005", 2025, "FIRST OF JUN"),
        _row("1,000", 2024, "FIRST OF SEP"),
    ]
    monkeypatch.setattr(cc, "http_get_json", lambda *a, **k: _nass_payload(rows))
    series = cc.fetch_nass_stocks_series(cc.NASS_STOCKS_SERIES["usda_wasde_stocks_to_use"])
    assert series[0] == 950.0     # oldest = Mar 2024
    assert series[-1] == 1300.0   # newest = Dec 2025


def test_handler_dedup_periode_premier_gagnant(monkeypatch):
    """Lignes multiples pour une même période (positions/classes) → dédoublonnées
    (premier gagnant), pas de double comptage qui fausserait le z-score."""
    rows = [
        _row("1,300", 2025, "FIRST OF DEC"),   # gardé
        _row("700", 2025, "FIRST OF DEC"),     # doublon période → ignoré
        _row("950", 2024, "FIRST OF MAR"),
        _row("1,000", 2024, "FIRST OF SEP"),
        _row("1,020", 2025, "FIRST OF SEP"),
    ]
    monkeypatch.setattr(cc, "http_get_json", lambda *a, **k: _nass_payload(rows))
    series = cc.fetch_nass_stocks_series(cc.NASS_STOCKS_SERIES["usda_wasde_stocks_to_use"])
    assert series.count(1300.0) == 1
    assert 700.0 not in series


def test_handler_sans_cle_na_propre(monkeypatch):
    """Sans USDA_API_KEY → None (n/a propre), motif nass_no_key, ZÉRO réseau."""
    monkeypatch.delenv("USDA_API_KEY", raising=False)
    called = {"n": 0}

    def _boom(*a, **k):
        called["n"] += 1
        return {"data": []}

    monkeypatch.setattr(cc, "http_get_json", _boom)
    out = cc._handle_nass_stocks("usda_wasde_stocks_to_use", _crit(), TS)
    assert out is None
    assert called["n"] == 0                    # pas d'appel réseau sans clé
    assert cc.SKIP_COUNTER.get("nass_no_key") == 1


def test_handler_api_ko_na_propre(monkeypatch):
    """API KO (http_get_json → None) → None (n/a propre), motif nass_dead."""
    monkeypatch.setattr(cc, "http_get_json", lambda *a, **k: None)
    out = cc._handle_nass_stocks("usda_wasde_stocks_to_use", _crit(), TS)
    assert out is None
    assert cc.SKIP_COUNTER.get("nass_dead") == 1


def test_handler_serie_trop_courte_na_propre(monkeypatch):
    """Moins de 4 points exploitables → None (n/a propre), pas de z-score bidon."""
    rows = [_row("950", 2024, "FIRST OF MAR"), _row("980", 2024, "FIRST OF JUN")]
    monkeypatch.setattr(cc, "http_get_json", lambda *a, **k: _nass_payload(rows))
    out = cc._handle_nass_stocks("usda_wasde_stocks_to_use", _crit(), TS)
    assert out is None
    assert cc.SKIP_COUNTER.get("nass_series_courte") == 1


def _now():
    from datetime import datetime, timezone
    return datetime(2026, 6, 10, 14, 0, tzinfo=timezone.utc)  # jour 10 → dans fenêtre
