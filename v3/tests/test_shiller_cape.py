"""Tests du scraper défensif Shiller CAPE (multpl.com) — critère sp500 id=8.

Fiche sp500.yml : cle_courante "shiller_cape_fwd_pe", normalisation "composite",
signe -1 (valorisation HAUTE → baissier ; le signe est appliqué par le scoring,
pas par le calculator — la valeur_normalisee émise ici est PRE-signe).

Couverture :
  (a) HTML valide → CAPE extrait + normalisé
  (b) valeur hors plage [5, 70] → n/a
  (c) échec réseau / parse → n/a (pas de crash)
  (d) override manuel présent → priorité sur le scraper
  (e) signe -1 respecté (CAPE élevé → valeur_normalisee positive → baissier
      après application du signe -1 par le scoring ; CAPE bas → négative)

AUCUN réseau réel : http_get_text et le fichier manuel sont mockés.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import criteres_calculator as cc  # noqa: E402


@pytest.fixture(autouse=True)
def _no_real_http(monkeypatch):
    """Bloque tout HTTP réel : un test qui oublie de mocker échoue proprement."""
    def _fail(*a, **kw):
        raise RuntimeError("HTTP réseau interdit dans les tests")

    monkeypatch.setattr(cc, "http_get_text", _fail)


# Référence à la VRAIE lecture manuelle, capturée avant tout monkeypatch.
_REAL_READ_MANUAL = cc._read_manual_shiller_cape


@pytest.fixture(autouse=True)
def _no_manual_override(monkeypatch):
    """Par défaut : pas de fichier d'override manuel (les tests qui le veulent
    le réactivent explicitement). Évite qu'un shiller_cape.json local pollue."""
    monkeypatch.setattr(cc, "_read_manual_shiller_cape", lambda: None)


@pytest.fixture
def now_fixed():
    return datetime(2026, 5, 29, 12, 0, tzinfo=timezone.utc)


def _cape_crit() -> dict:
    """Critère CAPE tel que fourni par la fiche sp500.yml (id=8)."""
    return {"cle_courante": "shiller_cape_fwd_pe", "normalisation": "composite",
            "source": "multpl / fournisseur valorisation", "cap": 1.0,
            "signe": -1, "poids": 4}


# Fragment HTML représentatif de multpl.com/shiller-pe (libellé + valeur).
_HTML_OK = """
<html><body>
  <div id="result">
    <strong>Current Shiller PE Ratio:</strong>
    <span class="value">35.12</span>
    <span class="unit">&nbsp;+0.05 (0.14%)</span>
  </div>
</body></html>
"""

_HTML_CHEAP = _HTML_OK.replace("35.12", "21.00")
_HTML_OUT_OF_RANGE = _HTML_OK.replace("35.12", "999.99")
_HTML_BROKEN = "<html><body><p>Page redesigned, no ratio label here.</p></body></html>"


# ---------------------------------------------------------------------------
# Couche parsing
# ---------------------------------------------------------------------------

def test_parse_html_valide():
    assert cc._parse_shiller_cape_html(_HTML_OK) == pytest.approx(35.12)


def test_parse_html_casse_renvoie_none():
    assert cc._parse_shiller_cape_html(_HTML_BROKEN) is None
    assert cc._parse_shiller_cape_html("") is None


# ---------------------------------------------------------------------------
# fetch_shiller_cape — scraper
# ---------------------------------------------------------------------------

def test_fetch_html_valide(monkeypatch):
    """(a) HTML valide → CAPE extrait."""
    monkeypatch.setattr(cc, "http_get_text", lambda url, **kw: _HTML_OK)
    assert cc.fetch_shiller_cape() == pytest.approx(35.12)


def test_fetch_valeur_hors_plage_na(monkeypatch):
    """(b) valeur hors plage [5, 70] → n/a (None), pas d'invention."""
    monkeypatch.setattr(cc, "http_get_text", lambda url, **kw: _HTML_OUT_OF_RANGE)
    assert cc.fetch_shiller_cape() is None


def test_fetch_reseau_ko_na(monkeypatch):
    """(c) réseau KO (http_get_text renvoie None) → n/a sans crash."""
    monkeypatch.setattr(cc, "http_get_text", lambda url, **kw: None)
    assert cc.fetch_shiller_cape() is None


def test_fetch_parse_ko_na(monkeypatch):
    """(c bis) page changée (parse KO) → n/a sans crash."""
    monkeypatch.setattr(cc, "http_get_text", lambda url, **kw: _HTML_BROKEN)
    assert cc.fetch_shiller_cape() is None


# ---------------------------------------------------------------------------
# Override manuel (filet) — priorité sur le scraper
# ---------------------------------------------------------------------------

def test_override_manuel_prioritaire(monkeypatch, tmp_path):
    """(d) override manuel présent → priorité sur le scraper (qui ne doit même
    pas être appelé)."""
    manual = tmp_path / "shiller_cape.json"
    manual.write_text('{"cape": 30.5}', encoding="utf-8")
    monkeypatch.setattr(cc, "SHILLER_CAPE_MANUAL", manual)
    # On lève la garde autouse pour exercer la VRAIE lecture manuelle.
    monkeypatch.setattr(cc, "_read_manual_shiller_cape", _REAL_READ_MANUAL)

    def _scraper_interdit(url, **kw):
        raise AssertionError("le scraper ne doit pas être appelé si override présent")

    monkeypatch.setattr(cc, "http_get_text", _scraper_interdit)
    assert cc.fetch_shiller_cape() == pytest.approx(30.5)


def test_override_manuel_hors_plage_ignore(monkeypatch, tmp_path):
    """Override manuel hors plage → ignoré, on retombe sur le scraper."""
    manual = tmp_path / "shiller_cape.json"
    manual.write_text('{"cape": 500}', encoding="utf-8")
    monkeypatch.setattr(cc, "SHILLER_CAPE_MANUAL", manual)
    monkeypatch.setattr(cc, "_read_manual_shiller_cape", _REAL_READ_MANUAL)
    monkeypatch.setattr(cc, "http_get_text", lambda url, **kw: _HTML_OK)
    assert cc.fetch_shiller_cape() == pytest.approx(35.12)


def test_override_manuel_fichier_invalide_ignore(monkeypatch, tmp_path):
    """Override manuel illisible (JSON cassé) → ignoré, fallback scraper, pas de crash."""
    manual = tmp_path / "shiller_cape.json"
    manual.write_text("{ pas du json", encoding="utf-8")
    monkeypatch.setattr(cc, "SHILLER_CAPE_MANUAL", manual)
    monkeypatch.setattr(cc, "_read_manual_shiller_cape", _REAL_READ_MANUAL)
    monkeypatch.setattr(cc, "http_get_text", lambda url, **kw: _HTML_OK)
    assert cc.fetch_shiller_cape() == pytest.approx(35.12)


# ---------------------------------------------------------------------------
# Branchement bout-en-bout via build_critere_value + signe -1
# ---------------------------------------------------------------------------

def test_build_critere_cape_cher_contribution_baissiere(monkeypatch, now_fixed):
    """(e) CAPE élevé (35.12 > neutre 28) → valeur_normalisee POSITIVE.
    Le scoring applique signe=-1 → contribution BAISSIÈRE. Cohérent fiche."""
    monkeypatch.setattr(cc, "fetch_shiller_cape", lambda: 35.12)
    val = cc.build_critere_value("sp500", _cape_crit(), {}, {}, [], now_fixed)
    assert val is not None, "le CAPE doit être branché dans _handle_composite"
    assert val["valeur"] == pytest.approx(35.12)
    assert val["valeur_normalisee"] > 0  # cher → positif (×signe -1 = baissier)
    # signe appliqué par le scoring → contribution finale négative (baissière)
    assert val["valeur_normalisee"] * _cape_crit()["signe"] < 0


def test_build_critere_cape_bon_marche_contribution_haussiere(monkeypatch, now_fixed):
    """CAPE bas (21 < neutre 28) → valeur_normalisee NÉGATIVE → ×signe -1 = haussier."""
    monkeypatch.setattr(cc, "fetch_shiller_cape", lambda: 21.0)
    val = cc.build_critere_value("sp500", _cape_crit(), {}, {}, [], now_fixed)
    assert val is not None
    assert val["valeur_normalisee"] < 0
    assert val["valeur_normalisee"] * _cape_crit()["signe"] > 0  # haussier


def test_build_critere_cape_na_si_indispo(monkeypatch, now_fixed):
    """fetch indispo (None) → critère n/a propre (None), pas de valeur figée."""
    monkeypatch.setattr(cc, "fetch_shiller_cape", lambda: None)
    val = cc.build_critere_value("sp500", _cape_crit(), {}, {}, [], now_fixed)
    assert val is None


def test_build_critere_cape_normalisee_capee(monkeypatch, now_fixed):
    """CAPE extrême (mais dans la plage, ex. 70) → normalisee capée à cap=1.0."""
    monkeypatch.setattr(cc, "fetch_shiller_cape", lambda: 70.0)
    val = cc.build_critere_value("sp500", _cape_crit(), {}, {}, [], now_fixed)
    assert val is not None
    assert val["valeur_normalisee"] == pytest.approx(1.0)
