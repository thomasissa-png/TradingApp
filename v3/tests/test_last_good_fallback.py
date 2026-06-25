"""Tests — Fallback « dernière valeur valide » des critères à source réseau.

Incident reproduit : le 2026-06-25 7h, le critère météo cacao le plus lourd
(`meteo_ci_ghana_precip_30j`, poids 11) est tombé en n/a sur une panne réseau
Open-Meteo → couverture cacao 41 % < 70 % → cacao écarté du Top 3 alors qu'il a
fait +7,13 % (meilleur move du jour).

Ce module prouve :
  - CAS CACAO RÉSOLU : météo KO (mock → None) + cache last-good frais →
    le critère est RÉSOLU (valeur reportée, reporte=True), plus n/a.
  - CAS N/A : météo KO + cache absent OU périmé (> plafond jours ouvrés) →
    le critère reste n/a (zéro invention).
  - PÉRIMÈTRE : prix/momentum/vol intraday EXCLUS du repli.
  - PLAFONDS PAR TYPE : météo 5j, COT 8j, taux/FX 3j.
  - PERSISTANCE : un succès mémorise la dernière bonne valeur.
  - GARDE-FOU CONVICTION : critère reporté = driver dominant → conviction
    plafonnée à « contestée » ; non-dominant → conviction « forte » conservée.

Aucun appel réseau réel. v3/data/ jamais pollué (tmp_path + cache injecté).
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
import last_good_cache as lgc  # noqa: E402

# Jeudi 2026-06-25 (le jour de l'incident), 5h UTC.
NOW = datetime(2026, 6, 25, 5, 0, tzinfo=timezone.utc)
CACAO_CLE = "meteo_ci_ghana_precip_30j"
CACAO_CRIT = {
    "cle_courante": CACAO_CLE,
    "normalisation": "zscore_abs",
    "source": "Open-Meteo",
    "zscore_div": 2,
    "cap": 1.0,
}


@pytest.fixture(autouse=True)
def _clean_state():
    cc.SKIP_COUNTER.clear()
    cc.REPORTED_COUNTER.clear()
    cc._LAST_GOOD_CACHE = {}
    # Le fallback n'est ACTIF que pendant run() en prod ; on l'arme ici pour
    # tester le chokepoint build_critere_value en appel direct.
    cc._LAST_GOOD_ENABLED = True
    yield
    cc.SKIP_COUNTER.clear()
    cc.REPORTED_COUNTER.clear()
    cc._LAST_GOOD_CACHE = {}
    cc._LAST_GOOD_ENABLED = False


# ---------------------------------------------------------------------------
# TEST CLÉ 1 — météo cacao KO + cache frais → RÉSOLU (valeur reportée)
# ---------------------------------------------------------------------------

def test_cacao_meteo_ko_avec_cache_frais_est_reporte(monkeypatch):
    """LE cas prouvé : Open-Meteo injoignable (None) MAIS cache last-good cacao
    frais (J-3 ouvrés) → le critère est RÉSOLU avec reporte=True, plus n/a."""
    # Open-Meteo en panne réseau (comme le 2026-06-25 05:23 UTC).
    monkeypatch.setattr(cc, "fetch_open_meteo_anomaly", lambda *a, **k: None)
    # Cache last-good : valeur cacao réellement observée 3 jours ouvrés avant
    # (lundi 2026-06-22 → jeudi 2026-06-25 = 3 jours ouvrés). Sous le plafond 5j.
    cc._LAST_GOOD_CACHE = {
        CACAO_CLE: {
            "valeur": 0.357,
            "valeur_normalisee": 0.42,
            "valeur_ponderee": 0.42,
            "date": "2026-06-22",
        }
    }
    res = cc.build_critere_value("cacao", CACAO_CRIT, {}, {}, [], NOW)
    assert res is not None, "le critère doit être RÉSOLU (plus n/a)"
    assert res["reporte"] is True
    assert res["reporte_age_j"] == 3
    assert res["valeur_normalisee"] == 0.42
    assert res["valeur"] == 0.357
    # Échec VISIBLE : la cause de l'échec source est annexée.
    assert "reporte_cause" in res
    # Comptabilisé pour le bloc « Valeurs reportées » de criteres-health.
    assert any(CACAO_CLE in k for k in cc.REPORTED_COUNTER)


# ---------------------------------------------------------------------------
# TEST CLÉ 2 — météo cacao KO SANS cache (ou cache périmé) → reste n/a
# ---------------------------------------------------------------------------

def test_cacao_meteo_ko_sans_cache_reste_na(monkeypatch):
    monkeypatch.setattr(cc, "fetch_open_meteo_anomaly", lambda *a, **k: None)
    cc._LAST_GOOD_CACHE = {}  # cache vide → zéro invention
    res = cc.build_critere_value("cacao", CACAO_CRIT, {}, {}, [], NOW)
    assert res is None, "cache vide → n/a (comportement actuel, zéro invention)"


def test_cacao_meteo_ko_cache_perime_reste_na(monkeypatch):
    """Cache présent mais TROP VIEUX (> 5 jours ouvrés pour la météo) → la valeur
    reportée EXPIRE → n/a (pas de valeur zombie)."""
    monkeypatch.setattr(cc, "fetch_open_meteo_anomaly", lambda *a, **k: None)
    # 2026-06-17 (mercredi) → 2026-06-25 (jeudi) = 6 jours ouvrés > plafond 5j.
    cc._LAST_GOOD_CACHE = {
        CACAO_CLE: {"valeur": 0.357, "valeur_normalisee": 0.42,
                    "valeur_ponderee": 0.42, "date": "2026-06-17"}
    }
    res = cc.build_critere_value("cacao", CACAO_CRIT, {}, {}, [], NOW)
    assert res is None, "cache périmé (>5j ouvrés) → n/a"


# ---------------------------------------------------------------------------
# Succès → mémorisation dans le cache (persistance)
# ---------------------------------------------------------------------------

def test_succes_meteo_memorise_last_good(monkeypatch):
    """Un calcul météo RÉUSSI range sa valeur dans le cache last-good."""
    monkeypatch.setattr(cc, "fetch_open_meteo_anomaly", lambda *a, **k: 0.84)
    cc._LAST_GOOD_CACHE = {}
    res = cc.build_critere_value("cacao", CACAO_CRIT, {}, {}, [], NOW)
    assert res is not None
    assert not res.get("reporte")  # valeur VIVANTE, pas reportée
    assert CACAO_CLE in cc._LAST_GOOD_CACHE
    entry = cc._LAST_GOOD_CACHE[CACAO_CLE]
    assert entry["date"] == "2026-06-25"
    assert entry["valeur"] == pytest.approx(0.84)


def test_un_report_nest_jamais_remis_au_cache(monkeypatch):
    """Une valeur REPORTÉE ne réécrit pas le cache (sinon l'âge se réinitialise
    et masque la panne durable)."""
    monkeypatch.setattr(cc, "fetch_open_meteo_anomaly", lambda *a, **k: None)
    cc._LAST_GOOD_CACHE = {
        CACAO_CLE: {"valeur": 0.357, "valeur_normalisee": 0.42,
                    "valeur_ponderee": 0.42, "date": "2026-06-22"}
    }
    res = cc.build_critere_value("cacao", CACAO_CRIT, {}, {}, [], NOW)
    assert res["reporte"] is True
    # La date du cache reste 2026-06-22 (pas réécrite à 2026-06-25).
    assert cc._LAST_GOOD_CACHE[CACAO_CLE]["date"] == "2026-06-22"


# ---------------------------------------------------------------------------
# PÉRIMÈTRE — prix/momentum/vol EXCLUS du repli
# ---------------------------------------------------------------------------

def test_momentum_prix_exclu_du_repli(monkeypatch):
    """Un critère momentum_prix (intraday, fallback Stooq propre) n'est JAMAIS
    reporté : son échec reste n/a même si une valeur traîne au cache."""
    crit = {"cle_courante": "momentum_prix_20j_cacao", "normalisation": "zscore",
            "source": "yfinance", "zscore_div": 2, "cap": 1.0}
    monkeypatch.setattr(cc, "fetch_twelve_series", lambda *a, **k: None)
    cc._LAST_GOOD_CACHE = {
        "momentum_prix_20j_cacao": {"valeur": 1.0, "valeur_normalisee": 0.5,
                                    "valeur_ponderee": 0.5, "date": "2026-06-24"}
    }
    res = cc.build_critere_value("cacao", crit, {}, {}, [], NOW)
    assert res is None, "momentum/prix EXCLU du repli (valeur périmée trompeuse)"


def test_eligibilite_inclusion_exclusion():
    # Inclus (sources réseau lentes)
    assert lgc.is_last_good_eligible("meteo_ci_ghana_precip_30j", {"source": "Open-Meteo"})
    assert lgc.is_last_good_eligible("cftc_cot_or_nets", {"source": "CFTC"})
    assert lgc.is_last_good_eligible("differentiel_taux_2y_us_de", {"source": "FRED"})
    assert lgc.is_last_good_eligible("balance_commerciale_ez", {"source": "Eurostat"})
    assert lgc.is_last_good_eligible("taux_reels_us", {"source": "FRED"})
    # Exclus (prix/momentum/vol intraday)
    assert not lgc.is_last_good_eligible("momentum_prix_7j_or", {"source": "Twelve"})
    assert not lgc.is_last_good_eligible("rsi_14j_gspc", {"source": "Twelve"})
    assert not lgc.is_last_good_eligible("niveau_vix_absolu", {"source": "Twelve"})
    assert not lgc.is_last_good_eligible("gap_rv_iv", {"source": "Twelve"})
    assert not lgc.is_last_good_eligible("term_structure_vix_vix3m", {"source": "CBOE"})
    assert not lgc.is_last_good_eligible("vix_regime", {"source": "Twelve"})


# ---------------------------------------------------------------------------
# PLAFONDS D'ÂGE PAR TYPE
# ---------------------------------------------------------------------------

def test_plafonds_age_par_type():
    assert lgc.max_age_for("meteo_ci_ghana_precip_30j") == 5
    assert lgc.max_age_for("cftc_cot_or_nets") == 8
    assert lgc.max_age_for("differentiel_taux_2y_us_de") == 3
    assert lgc.max_age_for("taux_reels_us", {"source": "FRED"}) == 3
    assert lgc.max_age_for("balance_commerciale_ez") == 5
    # Défaut pour une clé éligible non typée explicitement.
    assert lgc.max_age_for("indicateur_lent_inconnu") == lgc.LAST_GOOD_MAX_AGE_DAYS


def test_cot_tolere_8_jours_ouvres():
    """Le COT (hebdo) tolère un report jusqu'à 8 jours ouvrés."""
    cache = {"cftc_cot_or_nets": {"valeur": 1.2, "valeur_normalisee": 0.6,
                                  "valeur_ponderee": 0.6, "date": "2026-06-15"}}
    # 2026-06-15 (lundi) → 2026-06-25 (jeudi) = 8 jours ouvrés (≤ plafond COT 8).
    entry = lgc.lookup_fresh(cache, "cftc_cot_or_nets", NOW)
    assert entry is not None
    assert entry["age_business_days"] == 8
    assert entry["max_age_days"] == 8


def test_taux_expire_a_4_jours_ouvres():
    """Un taux (plafond 3j) reporté depuis 4 jours ouvrés EXPIRE → None."""
    cache = {"differentiel_taux_2y_us_de": {"valeur": 0.1, "valeur_normalisee": 0.2,
                                            "valeur_ponderee": 0.2, "date": "2026-06-19"}}
    # 2026-06-19 (vendredi) → 2026-06-25 (jeudi) = 4 jours ouvrés > plafond 3.
    entry = lgc.lookup_fresh(cache, "differentiel_taux_2y_us_de", NOW)
    assert entry is None


# ---------------------------------------------------------------------------
# JOURS OUVRÉS — week-end neutralisé
# ---------------------------------------------------------------------------

def test_business_days_neutralise_weekend():
    from datetime import date
    # vendredi → lundi = 1 jour ouvré (samedi/dimanche neutralisés)
    assert lgc._business_days_between(date(2026, 6, 19), date(2026, 6, 22)) == 1
    # même jour = 0
    assert lgc._business_days_between(date(2026, 6, 25), date(2026, 6, 25)) == 0
    # lundi → vendredi = 4 jours ouvrés
    assert lgc._business_days_between(date(2026, 6, 22), date(2026, 6, 26)) == 4
