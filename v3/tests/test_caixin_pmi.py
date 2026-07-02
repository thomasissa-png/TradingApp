"""Tests de l'extracteur Caixin Manufacturing PMI Chine depuis les news.

Vérifie le contrat de `criteres_calculator.extract_caixin_pmi` :
- extraction d'un nombre PMI plausible (séparateur '.' et ',')
- garde-fou de plage [35, 65] (rejette années, milliards, %)
- exclusion du PMI services et des autres pays que la Chine
- récence (news trop vieille ignorée)
- zéro invention : aucun nombre fiable → None (le critère reste n/a)

Aucun appel réseau : on teste la fonction pure sur des items news in-memory.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import criteres_calculator as cc  # noqa: E402

NOW = datetime(2026, 6, 3, 9, 0, tzinfo=timezone.utc)


def _news(trigger: str, *, l2: str = "", days_ago: int = 0,
          source: str = "investing_economy", news_zone: str = "CN") -> dict:
    """Construit un item event-log minimal (champs lus par _event_text/_dt)."""
    return {
        "trigger": trigger,
        "l2": l2,
        "l1": "",
        "source": source,
        "news_zone": news_zone,
        "_dt": NOW - timedelta(days=days_ago),
    }


# --- (a) extraction nominale --------------------------------------------------

def test_caixin_rose_to_value():
    """'Caixin Manufacturing PMI rose to 50.8 in May' → 50.8."""
    items = [_news("Caixin Manufacturing PMI rose to 50.8 in May")]
    assert cc.extract_caixin_pmi(items, NOW) == 50.8


def test_caixin_manufacturier_francais():
    """Libellé français avec virgule décimale → 51.2."""
    items = [_news("PMI manufacturier chinois (Caixin) à 51,2 en mai")]
    assert cc.extract_caixin_pmi(items, NOW) == 51.2


# --- (b) pas de chiffre → None ------------------------------------------------

def test_caixin_no_number_returns_none():
    """'China manufacturing PMI beats expectations' (sans chiffre) → None."""
    items = [_news("China manufacturing PMI beats expectations in May",
                   source="investing_economy")]
    assert cc.extract_caixin_pmi(items, NOW) is None


# --- (c) hors plage → ignoré --------------------------------------------------

def test_caixin_out_of_range_ignored():
    """'2026' et '75 billion' sont hors plage [35,65] → None (pas d'invention)."""
    items = [
        _news("China Caixin manufacturing PMI outlook for 2026 supported by "
              "75 billion yuan stimulus"),
    ]
    assert cc.extract_caixin_pmi(items, NOW) is None


def test_caixin_picks_plausible_over_year():
    """Un nombre plausible (49.5) coexistant avec '2026' → on prend 49.5."""
    items = [_news("Caixin China manufacturing PMI fell to 49.5 in 2026 survey")]
    assert cc.extract_caixin_pmi(items, NOW) == 49.5


# --- (d) PMI services → ignoré ------------------------------------------------

def test_caixin_services_ignored():
    """Le Caixin SERVICES PMI ne doit jamais alimenter le manufacturier."""
    items = [_news("Caixin China services PMI rose to 52.3 in May")]
    assert cc.extract_caixin_pmi(items, NOW) is None


# --- autres pays → ignorés ----------------------------------------------------

def test_other_country_manufacturing_pmi_ignored():
    """India/Japan/US manufacturing PMI ne doivent pas être confondus."""
    items = [
        _news("India manufacturing PMI rose to 58.4 in May", news_zone="Global"),
        _news("ISM Manufacturing PMI US at 51.0", news_zone="US"),
        _news("Japan factory PMI shows slowing growth at 49.1", news_zone="Global"),
    ]
    assert cc.extract_caixin_pmi(items, NOW) is None


def test_mixed_china_and_other_country_ignored():
    """Item mêlant Chine + autre pays → écarté (ambiguïté de valeur)."""
    items = [_news("Asia PMI: Chinese and Indian manufacturing both rose to 50.5")]
    assert cc.extract_caixin_pmi(items, NOW) is None


# --- (e) virgule décimale (déjà couvert) + (f) news trop vieille --------------

def test_old_news_ignored():
    """News au-delà de la fenêtre de récence → None (pas de vieille valeur)."""
    items = [_news("Caixin China manufacturing PMI rose to 50.8 in May",
                   days_ago=cc.CAIXIN_NEWS_MAX_AGE_DAYS + 5)]
    assert cc.extract_caixin_pmi(items, NOW) is None


def test_recent_news_within_window_accepted():
    """News dans la fenêtre de récence → acceptée."""
    items = [_news("Caixin China manufacturing PMI rose to 50.8",
                   days_ago=cc.CAIXIN_NEWS_MAX_AGE_DAYS - 1)]
    assert cc.extract_caixin_pmi(items, NOW) == 50.8


# --- priorité Caixin > NBS/official, puis récence -----------------------------

def test_caixin_priority_over_official():
    """Caixin (privé) prioritaire sur le NBS/official PMI même moins récent."""
    items = [
        _news("China official NBS manufacturing PMI at 49.0", days_ago=0,
              source="investing_economy"),
        _news("Caixin China manufacturing PMI rose to 50.8", days_ago=1),
    ]
    assert cc.extract_caixin_pmi(items, NOW) == 50.8


def test_official_fallback_when_no_caixin():
    """Sans Caixin, le NBS/official manufacturing PMI Chine sert de proxy."""
    items = [_news("China official manufacturing PMI rose to 50.4 in May")]
    assert cc.extract_caixin_pmi(items, NOW) == 50.4


# --- robustesse ---------------------------------------------------------------

def test_empty_list_returns_none():
    assert cc.extract_caixin_pmi([], NOW) is None


def test_string_items_supported():
    """Accepte aussi des strings brutes (pas seulement des dicts event-log)."""
    items = ["Caixin China manufacturing PMI rose to 50.8 in May"]
    assert cc.extract_caixin_pmi(items, NOW) == 50.8


# --- intégration : dispatch lineaire dans build_critere_value -----------------

def test_handler_emits_lineaire_dict_when_value_found():
    """En fenêtre + valeur trouvée → dict {valeur, ts} (format lineaire)."""
    crit = {"cle_courante": "caixin_pmi_manuf", "normalisation": "lineaire",
            "source": "news", "centre": 50}
    items = [_news("Caixin China manufacturing PMI rose to 50.8")]
    # now = 3 du mois → fenêtre d'activation (d <= 9) active
    out = cc.build_critere_value("cuivre", crit, {}, {}, items, NOW)
    assert out is not None
    assert out["valeur"] == 50.8


def test_handler_na_when_no_value():
    """En fenêtre mais aucune valeur fiable → None (n/a propre)."""
    crit = {"cle_courante": "caixin_pmi_manuf", "normalisation": "lineaire",
            "source": "news", "centre": 50}
    items = [_news("China manufacturing PMI beats expectations")]
    out = cc.build_critere_value("cuivre", crit, {}, {}, items, NOW)
    assert out is None


def test_handler_hors_fenetre_na_propre_pas_de_placeholder_degenere():
    """Hors fenêtre (jour > 9) SANS news fraîche → n/a PROPRE (None), JAMAIS le
    placeholder générique dégénéré {valeur_normalisee: 0.0} sans valeur brute.

    Régression : ce placeholder (valeur_normalisee-only pour un critère lineaire)
    était persisté puis passé au scoring, où float(None) échouait en
    « n/a (lineaire : valeur non numérique) » + « valeur 0 » affichée. caixin est
    extrait des news (récence-gated), il n'a pas de fenêtre horaire générique.
    """
    crit = {"cle_courante": "caixin_pmi_manuf", "normalisation": "lineaire",
            "source": "news", "centre": 50}
    later = datetime(2026, 6, 20, 9, 0, tzinfo=timezone.utc)  # jour 20 → hors fenêtre
    # news datée du 03/06 → hors récence (cutoff = 20/06 - 10j = 10/06) → rejetée
    items = [_news("Caixin China manufacturing PMI rose to 50.8")]
    out = cc.build_critere_value("cuivre", crit, {}, {}, items, later)
    assert out is None  # n/a propre, pas de dict {valeur_normalisee: 0.0}


def test_handler_hors_fenetre_extrait_news_fraiche():
    """Hors fenêtre mais news FRAÎCHE (récence OK) → extraction normale de la
    valeur brute. caixin n'a plus de gate mensuel : seule la récence compte."""
    crit = {"cle_courante": "caixin_pmi_manuf", "normalisation": "lineaire",
            "source": "news", "centre": 50}
    later = datetime(2026, 6, 20, 9, 0, tzinfo=timezone.utc)  # jour 20 → hors fenêtre
    fresh = {
        "trigger": "Caixin China manufacturing PMI rose to 50.8",
        "l2": "", "l1": "", "source": "investing_economy", "news_zone": "CN",
        "_dt": later - timedelta(days=1),  # récent vs `later`
    }
    out = cc.build_critere_value("cuivre", crit, {}, {}, [fresh], later)
    assert out is not None
    assert out["valeur"] == 50.8
    # jamais un placeholder dégénéré
    assert "note" not in out or out.get("note") != "hors fenêtre"
