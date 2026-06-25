"""Tests PARTIE B — Actus FRAÎCHES du jour dans les suivis 12h/18h (RSS léger).

Garde-fous prouvés :
- récolte RSS légère, ZÉRO DeepSeek (collect_light = titres bruts seulement)
- filtre par date : un titre antérieur au seuil (07h pour 12h, 12h pour 18h) est exclu
- dédup : un titre déjà montré (Contexte 7h ou frais du 12h) est exclu
- cas vide → message honnête « Pas de news fraîche notable depuis Xh. »
- fetch KO (collect_light qui lève) → dégradation propre, AUCUNE exception
- réseau JAMAIS appelé en test (collect_light toujours mocké)
- intégration build_suivi : bloc « Actus du jour » distinct du Contexte 7h
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import run_suivi as rs  # noqa: E402

PARIS = ZoneInfo("Europe/Paris")
UTC = timezone.utc


@dataclass
class FakeItem:
    title: str
    published: datetime
    source: str = "bbc_business"


def _utc(y, mo, d, h, mi=0):
    return datetime(y, mo, d, h, mi, tzinfo=UTC)


# ---------------------------------------------------------------------------
# Seuil de fraîcheur (UTC, DST géré par ZoneInfo)
# ---------------------------------------------------------------------------

def test_seuil_news_utc_12h_depuis_07h():
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    seuil = rs._seuil_news_utc("12h", now)
    # 07h00 Paris (CEST, UTC+2) = 05h00 UTC.
    assert seuil == _utc(2026, 6, 8, 5, 0)


def test_seuil_news_utc_18h_depuis_12h():
    now = datetime(2026, 6, 8, 18, 3, tzinfo=PARIS)
    seuil = rs._seuil_news_utc("18h", now)
    # 12h00 Paris (CEST) = 10h00 UTC.
    assert seuil == _utc(2026, 6, 8, 10, 0)


# ---------------------------------------------------------------------------
# Filtre par date : titre AVANT le seuil exclu
# ---------------------------------------------------------------------------

def test_filtre_date_exclut_titres_anciens():
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)  # seuil = 05h00 UTC
    items = [
        FakeItem("Brent rallies on OPEC cut talk", _utc(2026, 6, 8, 9, 0)),   # frais
        FakeItem("Old wheat report from yesterday", _utc(2026, 6, 7, 23, 0)),  # ancien
        FakeItem("Pre-open Fed note", _utc(2026, 6, 8, 4, 0)),                  # avant 05h
    ]
    lignes, titres, indispo = rs.recolte_news_fraiches(
        "12h", now, deja_vus=set(), collect_light=lambda: items
    )
    assert indispo is False
    assert len(lignes) == 1
    assert "Brent rallies" in lignes[0]
    assert titres == ["Brent rallies on OPEC cut talk"]


# ---------------------------------------------------------------------------
# Dédup : titre déjà vu exclu
# ---------------------------------------------------------------------------

def test_dedup_titre_deja_vu():
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    items = [
        FakeItem("Gold jumps on geopolitical risk", _utc(2026, 6, 8, 9, 0)),
        FakeItem("ECB holds rates steady", _utc(2026, 6, 8, 10, 0)),
    ]
    deja = {rs._normalize_titre("Gold jumps on geopolitical risk")}
    lignes, titres, _ = rs.recolte_news_fraiches(
        "12h", now, deja_vus=deja, collect_light=lambda: items
    )
    assert len(lignes) == 1
    assert "ECB holds rates" in lignes[0]
    assert all("Gold jumps" not in l for l in lignes)


def test_dedup_interne_meme_titre_deux_fois():
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    items = [
        FakeItem("Oil spikes after tanker incident", _utc(2026, 6, 8, 9, 0)),
        FakeItem("OIL SPIKES after tanker incident", _utc(2026, 6, 8, 9, 30)),  # casse différente
    ]
    lignes, _, _ = rs.recolte_news_fraiches(
        "12h", now, deja_vus=set(), collect_light=lambda: items
    )
    assert len(lignes) == 1  # dédup normalisée (casse)


# ---------------------------------------------------------------------------
# Cas vide → pas d'erreur, message honnête au rendu
# ---------------------------------------------------------------------------

def test_cas_vide():
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    lignes, titres, indispo = rs.recolte_news_fraiches(
        "12h", now, deja_vus=set(), collect_light=lambda: []
    )
    assert lignes == [] and titres == [] and indispo is False
    ctx = rs._ligne_contexte_frais("12h", lignes, indispo)
    assert ctx == "Rien de neuf depuis 7h."


# ---------------------------------------------------------------------------
# Fetch KO → dégradation propre, JAMAIS d'exception
# ---------------------------------------------------------------------------

def test_fetch_ko_degradation_propre():
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)

    def boom():
        raise ConnectionError("flux injoignable (conteneur sans réseau)")

    lignes, titres, indispo = rs.recolte_news_fraiches(
        "12h", now, deja_vus=set(), collect_light=boom
    )
    assert indispo is True
    assert lignes == [] and titres == []
    ctx = rs._ligne_contexte_frais("12h", lignes, indispo)
    assert ctx == "Actus du jour indisponibles (flux injoignable)."


def test_fetch_renvoie_none_degradation_propre():
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    _, _, indispo = rs.recolte_news_fraiches(
        "12h", now, deja_vus=set(), collect_light=lambda: None
    )
    assert indispo is True


# ---------------------------------------------------------------------------
# Top 1-3 max (suivi court)
# ---------------------------------------------------------------------------

def test_top_max_3():
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    items = [FakeItem(f"Fresh market headline number {i}", _utc(2026, 6, 8, 9, i))
             for i in range(10)]
    lignes, _, _ = rs.recolte_news_fraiches(
        "12h", now, deja_vus=set(), collect_light=lambda: items
    )
    assert len(lignes) == rs.MAX_NEWS_FRAICHES == 3
    # Tri fraîcheur desc : le plus récent (minute 9) d'abord.
    assert "number 9" in lignes[0]


# ---------------------------------------------------------------------------
# Snapshot titres frais : persistance + relecture (dédup 12h → 18h)
# ---------------------------------------------------------------------------

def test_snapshot_titres_roundtrip(tmp_path):
    titres = ["Brent rallies", "ECB holds rates"]
    rs.save_titres_frais_snapshot(date(2026, 6, 8), "12h", titres, base_dir=tmp_path)
    relus = rs.load_titres_frais_snapshot(date(2026, 6, 8), "12h", base_dir=tmp_path)
    assert relus == titres


def test_load_snapshot_absent_retourne_vide(tmp_path):
    assert rs.load_titres_frais_snapshot(date(2026, 6, 8), "12h", base_dir=tmp_path) == []


# ---------------------------------------------------------------------------
# Intégration build_suivi : bloc « Actus du jour » distinct du Contexte 7h
# ---------------------------------------------------------------------------

BULLETIN_7H = """# Bulletin 2026-06-08 07h

| Actif | 24h | 7j | 1m |
|---|---|---|---|
| Or | SHORT (-1.20) | SHORT (-0.80) | SHORT (-0.50) |
| CAC 40 | SHORT (-0.40) | LONG (+0.20) | LONG (+0.10) |
"""


def _fiche(actif, ticker, famille, seuil_24h):
    return {
        "actif": actif, "ticker_principal": ticker, "famille": famille,
        "seuils_reussite_pct": {"24h": seuil_24h, "7j": 1.3, "1m": 3.0},
    }


@pytest.fixture
def env(tmp_path):
    bdir = tmp_path / "bulletins"
    bdir.mkdir()
    (bdir / "bulletin-2026-06-08-07h.md").write_text(BULLETIN_7H, encoding="utf-8")
    odir = tmp_path / "prix-ouverture"
    odir.mkdir()
    (odir / "2026-06-08.json").write_text(
        json.dumps({"GC=F": 3400.0, "^FCHI": 8120.0}), encoding="utf-8")
    dlog = tmp_path / "decision-log"
    dlog.mkdir()
    sdir = tmp_path / "suivi"
    return {
        "bdir": bdir, "odir": odir, "dlog": dlog, "sdir": sdir,
        "fiches": {"or": _fiche("Or", "GC=F", "métaux-précieux", 0.5),
                   "cac40": _fiche("CAC 40", "^FCHI", "indices", 0.4)},
    }


def _build(env, report_type, now, collect_light):
    return rs.build_suivi(
        report_type, now=now, date_j=date(2026, 6, 8),
        bulletins_dir=env["bdir"], decision_log_dir=env["dlog"],
        suivi_dir=env["sdir"], prix_ouverture_dir=env["odir"],
        fiches=env["fiches"], fetch_price=lambda t: {"GC=F": 3410.0, "^FCHI": 8100.0}.get(t),
        collect_light=collect_light,
    )


def test_build_suivi_section_news_refondue(env):
    # FIX 2c (23/06) : les blocs « Actus du jour » (titres RSS bruts) et « Contexte
    # news (bulletin 7h) » sont SUPPRIMÉS du rendu. La section news ne garde que
    # « News des paris du jour » + « Grosses actualités depuis Xh ». La récolte RSS
    # continue d'alimenter les CHAMPS (snapshot dedup) mais n'est plus affichée.
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    items = [FakeItem("Brent rallies on OPEC cut talk", _utc(2026, 6, 8, 9, 0))]
    r = _build(env, "12h", now, collect_light=lambda: items)
    md = r.markdown
    assert "### Actus du jour" not in md
    assert "### Contexte news (bulletin 7h, non réactualisé)" not in md
    assert "### News des paris du jour" in md
    assert "### 🚨 Grosses actualités depuis 7h" in md
    # Le champ news_fraiches reste alimenté (snapshot dedup) mais non rendu.
    assert "Brent rallies on OPEC cut talk" not in md
    # Aucune mention MONÉTAIRE (WIN RATE ONLY). « gain » / « perte » = amplitude
    # directionnelle, autorisée depuis la décision fondateur 24/06 (« max gain » =
    # % vers la cible turbo > 1 %, jamais un montant). Seuls les vrais marqueurs
    # monétaires restent interdits.
    for tok in ("€", "$", "rendement", "p&l", "expectancy", "equity"):
        assert tok not in md.lower()


def test_build_suivi_actus_indispo_si_fetch_ko(env):
    # FIX 2c : le fetch RSS KO ne casse pas le suivi et n'affiche plus de message
    # « Actus du jour indisponibles » (bloc supprimé). Le champ indispo reste posé.
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)

    def boom():
        raise TimeoutError("réseau coupé")

    r = _build(env, "12h", now, collect_light=boom)
    assert r.news_fraiches_indispo is True
    assert "Actus du jour indisponibles (flux injoignable)." not in r.markdown
    assert "### News des paris du jour" in r.markdown


def test_build_suivi_actus_vide(env):
    # FIX 2c : plus de bloc « Actus du jour » → plus de message « Pas de news
    # fraîche notable ». La section news refondue reste présente.
    now = datetime(2026, 6, 8, 12, 3, tzinfo=PARIS)
    r = _build(env, "12h", now, collect_light=lambda: [])
    assert "Pas de news fraîche notable depuis 7h." not in r.markdown
    assert "### News des paris du jour" in r.markdown


def test_18h_dedup_contre_frais_du_12h(env):
    # FIX 2c : le bloc « Actus du jour » n'est plus rendu. On vérifie que la récolte
    # 18h continue de dédupliquer contre les titres frais persistés au 12h (champ
    # news_fraiches), même si non affiché — la persistance reste fonctionnelle.
    titre_12h = FakeItem("Gold jumps on geopolitical risk", _utc(2026, 6, 8, 9, 0))
    _build(env, "12h", datetime(2026, 6, 8, 12, 3, tzinfo=PARIS),
           collect_light=lambda: [titre_12h])
    items_18h = [
        FakeItem("Gold jumps on geopolitical risk", _utc(2026, 6, 8, 9, 0)),     # déjà vu
        FakeItem("US stocks open higher after CPI", _utc(2026, 6, 8, 14, 0)),     # nouveau
    ]
    r18 = _build(env, "18h", datetime(2026, 6, 8, 18, 3, tzinfo=PARIS),
                 collect_light=lambda: items_18h)
    titres_frais = [t for t in r18.news_fraiches]
    # Le nouveau titre est retenu, l'ancien (déjà vu au 12h) est dédupliqué.
    assert any("US stocks open higher after CPI" in l for l in titres_frais)
    assert not any("Gold jumps on geopolitical risk" in l for l in titres_frais)
    # Plus aucun bloc « Actus du jour » dans le rendu.
    assert "### Actus du jour" not in r18.markdown


def test_build_suivi_cablage_par_defaut(env, monkeypatch):
    # Garde-fou : si collect_light n'est PAS fourni, build_suivi importe
    # news_collector.collect_rss_light. On stub `news_collector` dans sys.modules
    # (le vrai module dépend de feedparser, absent du conteneur de test — L024) pour
    # prouver le câblage par défaut SANS toucher au réseau réel ni à feedparser.
    # FIX 2c : le titre frais n'est plus rendu → on prouve le câblage via le CHAMP.
    import types as _types
    stub = _types.ModuleType("news_collector")
    stub.collect_rss_light = lambda *a, **k: [
        FakeItem("Mocked fresh headline", _utc(2026, 6, 8, 9, 0))
    ]
    monkeypatch.setitem(sys.modules, "news_collector", stub)
    r = rs.build_suivi(
        "12h", now=datetime(2026, 6, 8, 12, 3, tzinfo=PARIS), date_j=date(2026, 6, 8),
        bulletins_dir=env["bdir"], decision_log_dir=env["dlog"], suivi_dir=env["sdir"],
        prix_ouverture_dir=env["odir"], fiches=env["fiches"],
        fetch_price=lambda t: 3410.0,
    )
    assert any("Mocked fresh headline" in l for l in r.news_fraiches)


def test_build_suivi_degrade_si_news_collector_absent(env, monkeypatch):
    # Si l'import de collect_rss_light échoue (feedparser absent en prod aussi),
    # la récolte dégrade proprement (indispo) sans crash — suivi hors-ligne OK.
    import builtins
    real_import = builtins.__import__

    def boom(name, *a, **k):
        if name == "news_collector":
            raise ModuleNotFoundError("No module named 'feedparser'")
        return real_import(name, *a, **k)

    monkeypatch.delitem(sys.modules, "news_collector", raising=False)
    monkeypatch.setattr(builtins, "__import__", boom)
    r = rs.build_suivi(
        "12h", now=datetime(2026, 6, 8, 12, 3, tzinfo=PARIS), date_j=date(2026, 6, 8),
        bulletins_dir=env["bdir"], decision_log_dir=env["dlog"], suivi_dir=env["sdir"],
        prix_ouverture_dir=env["odir"], fiches=env["fiches"],
        fetch_price=lambda t: 3410.0,
    )
    assert r.news_fraiches_indispo is True
