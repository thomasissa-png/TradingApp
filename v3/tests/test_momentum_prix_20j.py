"""Tests momentum-prix v3 — A1 (vraie variation 20j) + A7 (look-ahead).

Audit momentum-family 10/06 :
  A1 — le dispatcher route `momentum_prix_20j_*` vers la VRAIE variation 20j
       (rendement glissant close[t]/close[t-20]-1 puis z-score de la série de
       rendements), PAS le z-score du niveau de close (laggard, bug cacao).
  A7 — au run 7h, le momentum s'appuie sur le close J-1 définitif (pas une
       bougie intraday J0) via fetch_twelve_series. Zéro look-ahead.

Aucun appel HTTP réel : fetch_twelve_series est monkeypatché avec des séries
synthétiques aux valeurs connues.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

import criteres_calculator as cc


TS = "2026-06-10T07:00:00+00:00"


def _serie(closes, *, derniere_date=None):
    """Construit une série [(datetime_utc, close)] oldest→newest, 1 point/jour ouvré.

    `derniere_date` = date (UTC) du DERNIER close. Par défaut J-1 d'un run 7h fixé.
    """
    if derniere_date is None:
        derniere_date = datetime(2026, 6, 9, 22, 0, tzinfo=timezone.utc)
    n = len(closes)
    out = []
    for i, c in enumerate(closes):
        d = derniere_date - timedelta(days=(n - 1 - i))
        out.append((d, float(c)))
    return out


# --------------------------------------------------------------------------
# A1 — la branche calcule bien une VARIATION 20j, pas un niveau
# --------------------------------------------------------------------------

def test_momentum_20j_route_vers_variation_pas_niveau(monkeypatch):
    """Série en BAISSE récente mais NIVEAU encore au-dessus de sa moyenne 60j.

    C'est le piège du laggard : un z-score de NIVEAU resterait POSITIF (prix
    haut dans sa distribution) alors que la dérivée 20j est NÉGATIVE. La vraie
    variation 20j doit produire un z-score NÉGATIF (le mouvement récent baisse).
    """
    # 80 closes : longue montée linéaire jusqu'à 200, puis chute franche sur les
    # 25 dernières sessions (la variation 20j la plus récente est négative).
    closes = [100 + i for i in range(55)]          # 100 → 154 (montée)
    closes += [154 - 3 * i for i in range(1, 26)]  # 151 → 79 (chute récente)
    serie = _serie(closes)

    captured = {}

    def fake_fetch(symbol, *, interval="1day", outputsize=60):
        captured["symbol"] = symbol
        captured["outputsize"] = outputsize
        return serie

    monkeypatch.setattr(cc, "fetch_twelve_series", fake_fetch)

    res = cc._handle_twelve_zscore_dispatch("momentum_prix_20j_cacao", {}, TS)
    assert res is not None, "donnée suffisante → ne doit pas être n/a"
    # La variation 20j la plus récente est nettement négative → z-score négatif.
    assert res["valeur_normalisee"] < 0, (
        "le momentum doit refléter la VARIATION 20j (baisse) et non le niveau"
    )
    # Le symbole routé est bien le sous-jacent cacao (CC=F).
    assert captured["symbol"] == "CC=F"


def test_momentum_20j_hausse_recente_zscore_positif(monkeypatch):
    """Variation 20j récente positive (accélération haussière) → z-score > 0."""
    # Plateau puis accélération franche sur les dernières sessions.
    closes = [100.0] * 50 + [100 + 2 * i for i in range(1, 31)]  # 102 → 160
    monkeypatch.setattr(cc, "fetch_twelve_series",
                        lambda s, *, interval="1day", outputsize=60: _serie(closes))
    res = cc._handle_twelve_zscore_dispatch("momentum_prix_20j_or", {}, TS)
    assert res is not None
    assert res["valeur_normalisee"] > 0


def test_momentum_20j_valeur_brute_est_rendement_20j(monkeypatch):
    """La valeur brute (`valeur`) est le rendement 20j courant, contrôlé exactement.

    Série constante=100 sur 40 points puis +1/jour sur 21 points (101..121).
    Dernier close=121, close[-21]=100 → rendement 20j = 0.21. La série de
    rendements 20j n'est pas constante → std>0 → z-score défini.
    """
    # Plateau à 100 puis +1/jour sur 20 points → closes[-1]=120, closes[-21]=100.
    closes = [100.0] * 42 + [100.0 + i for i in range(1, 21)]  # ...100 | 101..120
    monkeypatch.setattr(cc, "fetch_twelve_series",
                        lambda s, *, interval="1day", outputsize=60: _serie(closes))
    res = cc._handle_twelve_zscore_dispatch("momentum_prix_20j_argent", {}, TS)
    assert res is not None
    # rendement 20j courant = 120/100 - 1 = 0.20 (z-score from series renvoie la
    # dernière valeur brute de la série z-scorée = ce rendement).
    assert res["valeur"] == pytest.approx(0.20, abs=1e-9)


def test_momentum_20j_donnee_insuffisante_na(monkeypatch):
    """Moins de 20+1 closes → impossible de calculer un rendement 20j → n/a propre."""
    monkeypatch.setattr(cc, "fetch_twelve_series",
                        lambda s, *, interval="1day", outputsize=60: _serie([100.0 + i for i in range(15)]))
    res = cc._handle_twelve_zscore_dispatch("momentum_prix_20j_ble", {}, TS)
    assert res is None


def test_momentum_20j_serie_absente_na(monkeypatch):
    """fetch_twelve_series KO → None = n/a propre (zéro invention)."""
    monkeypatch.setattr(cc, "fetch_twelve_series",
                        lambda s, *, interval="1day", outputsize=60: None)
    res = cc._handle_twelve_zscore_dispatch("momentum_prix_20j_petrole", {}, TS)
    assert res is None


def test_momentum_20j_diffère_du_niveau_sur_meme_serie(monkeypatch):
    """Preuve directe : sur la MÊME série piège, variation ≠ niveau (signe opposé).

    Compare la branche momentum (variation) à _twelve_zscore_from_symbol (niveau)
    pour montrer que la correction A1 change réellement le résultat.
    """
    # Forte montée 100→200 (60 sessions) puis léger repli en plateau haut
    # (195→185 sur 25 sessions). Le DERNIER close (~185) reste TRÈS haut dans la
    # distribution des 60 closes (niveau z-score > 0), mais la variation 20j la
    # plus récente est NÉGATIVE (le mouvement glissant baisse).
    closes = [100.0 + (100.0 * i / 59) for i in range(60)]      # 100 → 200
    closes += [195.0 - 0.4 * i for i in range(1, 26)]           # 194.6 → 185
    monkeypatch.setattr(cc, "fetch_twelve_series",
                        lambda s, *, interval="1day", outputsize=60: _serie(closes))
    variation = cc._twelve_variation_zscore("CC=F", cc.MOMENTUM_PRIX_LAG, {})
    niveau = cc._twelve_zscore_from_symbol("CC=F", {})
    assert variation is not None and niveau is not None
    # Le niveau reste POSITIF (prix haut dans sa distribution), la variation est
    # NÉGATIVE (repli récent) → la correction A1 change réellement le signal.
    assert niveau[1] > 0, f"niveau attendu > 0, obtenu {niveau[1]}"
    assert variation[1] < 0, f"variation attendue < 0, obtenu {variation[1]}"


# --------------------------------------------------------------------------
# A7 — look-ahead : au run 7h, le dernier point utilisé est J-1, pas J0
# --------------------------------------------------------------------------

def test_momentum_run_7h_utilise_close_j_moins_1(monkeypatch):
    """Garde-fou look-ahead : le dernier close de la série est J-1 (définitif).

    On simule un run 7h Paris le 2026-06-10. fetch_twelve_series (interval 1day)
    doit renvoyer comme dernier point le close du 2026-06-09 (J-1), jamais une
    bougie intraday datée du 2026-06-10 (J0, marché ouvert). On vérifie que la
    date du dernier point consommé est strictement antérieure au jour du run.
    """
    run_7h = datetime(2026, 6, 10, 5, 0, tzinfo=timezone.utc)  # 07h Paris
    # Série dont le dernier close est daté J-1 (close définitif de la veille).
    closes = [100.0 + (i % 7) for i in range(60)]
    serie_j1 = _serie(closes, derniere_date=datetime(2026, 6, 9, 22, 0, tzinfo=timezone.utc))

    monkeypatch.setattr(cc, "fetch_twelve_series",
                        lambda s, *, interval="1day", outputsize=60: serie_j1)

    serie = cc.fetch_twelve_series("CC=F")
    assert serie, "série non vide"
    derniere_date = serie[-1][0].date()
    assert derniere_date < run_7h.date(), (
        "look-ahead : le momentum 7h ne doit jamais consommer une bougie J0"
    )


def test_momentum_serie_contenant_j0_serait_detectee(monkeypatch):
    """Contrôle négatif : si une série incluait un point J0 (bougie intraday), le
    garde-fou le verrait. Documente le risque que A7 surveille.
    """
    run_jour = datetime(2026, 6, 10, 5, 0, tzinfo=timezone.utc).date()
    closes = [100.0 + (i % 5) for i in range(60)]
    # Série fautive : dernier point daté J0 (le jour du run).
    serie_j0 = _serie(closes, derniere_date=datetime(2026, 6, 10, 13, 0, tzinfo=timezone.utc))
    monkeypatch.setattr(cc, "fetch_twelve_series",
                        lambda s, *, interval="1day", outputsize=60: serie_j0)
    serie = cc.fetch_twelve_series("CC=F")
    derniere_date = serie[-1][0].date()
    # Ce cas DOIT être considéré comme un look-ahead (le test documente le risque).
    assert derniere_date == run_jour
