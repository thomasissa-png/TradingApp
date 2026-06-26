"""Nouveaux actifs 2026-06-26 — USD/JPY · Coton · Sucre.

Vérifie que les 3 fiches sont enregistrées (15 actifs au total), que leur
câblage de sources est résolu OU n/a propre (zéro crash, zéro invention), et que
`score_actif` produit une conclusion LONG/SHORT cohérente avec le signe des
critères.

Garde-fous : fiche stem == clé interne identique partout (leçon CAC) ; clés
uniques (L023) ; WIN RATE ONLY.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import criteres_calculator as cc  # noqa: E402
import scoring_analyste as sa  # noqa: E402

NOW = datetime(2026, 6, 26, 7, 0, tzinfo=timezone.utc)
NOUVEAUX = ["usdjpy", "coton", "sucre"]


def _mock_vals(fiche: dict, val: float) -> dict:
    """Valeurs normalisées mock pour TOUS les critères non-gate de la fiche.

    Permet d'exercer score_actif sans appels réseau (pas de clés API en CI).
    """
    out = {}
    for c in fiche.get("criteres", []):
        if c.get("normalisation") == "gate":
            continue
        cle = c["cle_courante"]
        v = 1.0 if c.get("normalisation") == "triplet" else val
        out[cle] = {
            "valeur": v,
            "valeur_normalisee": v,
            "valeur_ponderee": v,
            "ts": NOW.isoformat(),
        }
    return out


def test_15_actifs_enregistres():
    fiches = cc.load_fiches()
    assert len(fiches) == 15
    for k in NOUVEAUX:
        assert k in fiches, f"{k} non enregistré (fiche stem == clé interne)"


@pytest.mark.parametrize("key", NOUVEAUX)
def test_fiche_stem_egale_cle_interne(key):
    """Le nom de fichier == clé interne (anti-piège CAC `cac_40`/`cac40`)."""
    f = ROOT / "config" / "fiches" / f"{key}.yml"
    assert f.exists()
    assert f.stem == key


@pytest.mark.parametrize("key", NOUVEAUX)
def test_score_sans_donnee_ne_crashe_pas(key):
    """Valeurs vides => tout n/a => abstention propre (INSUFFISANT), pas de crash."""
    fiches = cc.load_fiches()
    res = sa.score_actif(key, fiches[key], {}, now=NOW)
    for h in ("24h", "7j", "1m"):
        assert res.conclusions[h] in ("LONG", "SHORT", "INSUFFISANT")


@pytest.mark.parametrize("key", NOUVEAUX)
def test_score_positif_donne_long(key):
    fiches = cc.load_fiches()
    res = sa.score_actif(key, fiches[key], _mock_vals(fiches[key], 0.8), now=NOW)
    for h in ("24h", "7j", "1m"):
        assert res.conclusions[h] == "LONG"


@pytest.mark.parametrize("key", NOUVEAUX)
def test_score_negatif_donne_short(key):
    fiches = cc.load_fiches()
    res = sa.score_actif(key, fiches[key], _mock_vals(fiches[key], -0.8), now=NOW)
    for h in ("24h", "7j", "1m"):
        assert res.conclusions[h] == "SHORT"


def test_cles_sources_cablees():
    """Chaque critère sourçable des 3 fiches est résolu par un dispatcher connu
    (CFTC / FRED / METEO / TWELVE / triplet / gate) — sinon n/a propre, jamais
    inventé."""
    fiches = cc.load_fiches()
    cftc = set(cc.CFTC_MARKETS)
    fred = set(cc.FRED_SPREADS) | set(cc.FRED_SERIES_SIMPLE)
    meteo = set(cc.METEO_CRITERIA)
    twelve = set(cc.TWELVE_SYMBOLS)
    for key in NOUVEAUX:
        for c in fiches[key]["criteres"]:
            cle = c["cle_courante"]
            norm = c.get("normalisation")
            if norm in ("triplet", "gate"):
                continue  # résolus par triggers_classifier / _resolve_gate
            if norm == "zscore_abs":
                assert cle in meteo, f"{key}:{cle} zscore_abs non mappé METEO"
                continue
            # zscore numérique : doit être dans un dispatcher OU déclaré manuel/USDA
            cablee = cle in cftc or cle in fred or cle in meteo or cle in twelve
            manuel = "manuel" in (c.get("source") or "").lower() or "usda" in (
                c.get("source") or "").lower()
            assert cablee or manuel, (
                f"{key}:{cle} ni câblé ni déclaré manuel/USDA — risque d'invention"
            )


def test_cftc_markets_nouveaux():
    """Noms CFTC exacts vérifiés sur Socrata (zéro invention)."""
    assert cc.CFTC_MARKETS["cftc_cot_jpy_nets"] == "JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE"
    assert cc.CFTC_MARKETS["cftc_cot_cotton"] == "COTTON NO. 2 - ICE FUTURES U.S."
    assert cc.CFTC_MARKETS["cftc_cot_sugar"] == "SUGAR NO. 11 - ICE FUTURES U.S."


def test_fred_spreads_jp():
    """Spread JP câblé sur IRLTLT01JPM156N (id FRED vérifié, pas le typo IRGT...)."""
    assert cc.FRED_SPREADS["diff_taux_10y_us_jp"] == ("DGS10", "IRLTLT01JPM156N")
    assert cc.FRED_SPREADS["diff_taux_2y_us_jp"] == ("DGS2", "IRLTLT01JPM156N")
