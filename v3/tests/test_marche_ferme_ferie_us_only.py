"""Fix « férié US-only » (2026-06-19, Juneteenth) — garde-fou périmètre.

Contexte : le 19/06/2026 (Juneteenth) le NYSE est FERMÉ mais Euronext (CAC) et
les marchés CONTINUS (or, pétrole, EUR/USD, cacao, café, blé…) cotent. L'ancienne
garde `is_trading_day` (NYSE OU Euronext fermé ⇒ NO-OP total) supprimait TOUT le
briefing à tort (~8×/an). Deux corrections sont testées ici :

PARTIE 1 — `is_any_market_open` : le cycle TOURNE tant qu'au moins un marché de
l'univers est ouvert. NO-OP COMPLET seulement si TOUT est fermé (week-end OU
férié global type Noël/Nouvel An).

PARTIE 2 — périmètre de mesure par actif : un call dont le marché était FERMÉ sur
la fenêtre mesurée (S&P/Nasdaq/VIX un férié US) n'est PAS jugé (statut
`marche-ferme`, exclu des KPIs), tandis que les continus + CAC sont mesurés.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import journaliste as jr  # noqa: E402

# Dates de référence (calendrier 2026).
JUNETEENTH = date(2026, 6, 19)      # vendredi — NYSE fermé, Euronext + continus ouverts
NOEL = date(2026, 12, 25)           # vendredi — TOUTES places fermées (férié global)
SAMEDI = date(2026, 6, 6)           # week-end
MARDI_ORDINAIRE = date(2026, 6, 9)  # jour ouvré normal

_HAS_HOLIDAYS = False
try:  # pragma: no cover - dépend de l'environnement
    import holidays as _probe  # noqa: F401

    _HAS_HOLIDAYS = True
except ImportError:  # pragma: no cover
    _HAS_HOLIDAYS = False

requires_lib = pytest.mark.skipif(
    not _HAS_HOLIDAYS,
    reason="lib `holidays` absente — distinction US/EU/continu indisponible (fallback union)",
)


# ===========================================================================
# PARTIE 1 — is_any_market_open (garde de run)
# ===========================================================================

def test_weekend_aucun_marche_ouvert() -> None:
    assert SAMEDI.weekday() == 5
    assert jr.is_any_market_open(SAMEDI) is False
    assert jr.is_any_market_open(date(2026, 6, 7)) is False  # dimanche


def test_jour_ouvre_ordinaire_au_moins_un_marche_ouvert() -> None:
    assert jr.is_any_market_open(MARDI_ORDINAIRE) is True


@requires_lib
def test_ferie_us_only_juneteenth_au_moins_un_marche_ouvert() -> None:
    # LE CAS FONDATEUR : NYSE fermé mais Euronext + continus cotent → on TOURNE.
    assert JUNETEENTH in jr.MARKET_HOLIDAYS  # connu du socle (union)
    assert jr.is_market_open_for("us", JUNETEENTH) is False    # NYSE fermé
    assert jr.is_market_open_for("eu", JUNETEENTH) is True     # Euronext ouvert
    assert jr.is_market_open_for("continu", JUNETEENTH) is True  # or/pétrole/FX cotent
    assert jr.is_any_market_open(JUNETEENTH) is True


def test_ferie_global_noel_aucun_marche_ouvert() -> None:
    # Noël : NYSE ET Euronext fermés → continus aussi (férié global) → NO-OP total.
    assert jr.is_market_open_for("us", NOEL) is False
    assert jr.is_market_open_for("eu", NOEL) is False
    assert jr.is_market_open_for("continu", NOEL) is False
    assert jr.is_any_market_open(NOEL) is False


def test_is_market_open_for_groupe_inconnu_ferme() -> None:
    # Zéro invention : groupe None / inconnu → fermé (l'appelant skippe).
    assert jr.is_market_open_for(None, MARDI_ORDINAIRE) is False
    assert jr.is_market_open_for("xxx", MARDI_ORDINAIRE) is False


def test_is_any_market_open_ne_prend_que_d() -> None:
    import inspect

    assert list(inspect.signature(jr.is_any_market_open).parameters) == ["d"]


# ===========================================================================
# PARTIE 2 — périmètre de mesure par actif (SKIP marché fermé)
# ===========================================================================

# Fiches RÉELLES (extraits config/fiches/*.yml) couvrant les 3 groupes.
FICHE_SP500 = {
    "actif": "S&P 500", "ticker_principal": "^GSPC", "famille": "indices",
    "seuils_reussite_pct": {"24h": 0.5, "7j": 1.5, "1m": 4.0},
}
FICHE_CAC = {
    "actif": "CAC 40", "ticker_principal": "^FCHI", "famille": "indices",
    "seuils_reussite_pct": {"24h": 0.5, "7j": 1.5, "1m": 4.0},
}
FICHE_OR = {
    "actif": "Or", "ticker_principal": "GC=F", "famille": "métaux-précieux",
    "seuils_reussite_pct": {"24h": 0.5, "7j": 1.3, "1m": 3.0},
}

# Override config : désambiguïse CAC (eu) vs S&P (us) — les deux sont famille
# "indices". On l'injecte via load_suivi_config monkeypatché (cf. fixture).
SUIVI_OVERRIDE = {"group_overrides_by_actif": {"CAC 40": "eu", "S&P 500": "us"}}


@pytest.fixture
def _suivi_override(monkeypatch):
    """Force les overrides de groupe (CAC=eu, S&P=us) sans dépendre du fichier."""
    import mesure_ouverture as mo  # noqa: PLC0415

    monkeypatch.setattr(mo, "load_suivi_config", lambda *a, **k: SUIVI_OVERRIDE)


def _setup_7j_juneteenth(tmp_path, fiche, ticker, actif_label):
    """Bulletin 7h avec un call LONG 7j dont l'échéance tombe le 19/06 (Juneteenth).

    7j = horizon CALENDAIRE → echeance = bulletin_date + 7. On choisit donc
    bulletin_date = 12/06/2026 pour que echeance == 19/06/2026 (Juneteenth).
    """
    bdate = date(2026, 6, 12)
    assert jr.compute_echeance(bdate, "7j") == JUNETEENTH
    bulletins = tmp_path / "bulletins"
    prix_emis = tmp_path / "prix-emission"
    prix_ouv = tmp_path / "prix-ouverture"
    bulletins.mkdir(parents=True, exist_ok=True)
    (bulletins / f"bulletin-{bdate.isoformat()}-07h.md").write_text(
        f"# Bulletin — {bdate.isoformat()}\n\n## Matrice\n\n"
        "| Actif | 24h | 7j | 1m |\n|---|---|---|---|\n"
        f"| {actif_label} | LONG (+2.0) | LONG (+2.0) | LONG (+2.0) |\n",
        encoding="utf-8",
    )
    prix_emis.mkdir()
    (prix_emis / f"{bdate.isoformat()}-07h.json").write_text(json.dumps({ticker: 100.0}))
    prix_ouv.mkdir()
    (prix_ouv / f"{bdate.isoformat()}.json").write_text(json.dumps({ticker: 100.0}))
    return bdate, bulletins, prix_emis, prix_ouv


def _measure_7j(tmp_path, fiche, fiche_key, ticker, actif_label, *, close):
    _, bulletins, prix_emis, prix_ouv = _setup_7j_juneteenth(
        tmp_path, fiche, ticker, actif_label
    )
    measures, _ = jr.measure(
        today=JUNETEENTH, bulletins_dir=bulletins, prix_emission_dir=prix_emis,
        prix_ouverture_dir=prix_ouv, fiches={fiche_key: fiche},
        fetch_price=lambda t: close,
    )
    sevenj = [m for m in measures if m.horizon == "7j"]
    assert len(sevenj) == 1
    return sevenj[0]


@requires_lib
def test_sp500_7j_juneteenth_skip_marche_ferme(tmp_path, _suivi_override):
    """S&P (us) un férié US : marché FERMÉ le jour d'échéance → NON jugé."""
    m = _measure_7j(
        tmp_path, FICHE_SP500, "sp500", "^GSPC", "S&P 500", close=104.0,
    )
    assert m.outcome == jr.OUTCOME_MARCHE_FERME
    assert m.outcome not in (jr.OUTCOME_VRAI, jr.OUTCOME_FAUSSE, jr.OUTCOME_NC)
    assert "marché us fermé" in m.note
    # Exclu des KPIs comme un suivi-interrompu (pas de mesure dégénérée).
    kpi = jr.compute_kpi([m])
    assert kpi.n_total == 0
    assert kpi.n_vrai == 0 and kpi.n_fausse == 0 and kpi.n_nc == 0


@requires_lib
def test_cac_7j_juneteenth_mesure_normalement(tmp_path, _suivi_override):
    """CAC (eu) un férié US : Euronext OUVERT → mesuré normalement (VRAI ici)."""
    m = _measure_7j(
        tmp_path, FICHE_CAC, "cac40", "^FCHI", "CAC 40", close=104.0,
    )
    # 100 → 104 = +4 % > seuil 1.5 %, LONG → VRAI. Surtout PAS marche-ferme.
    assert m.outcome == jr.OUTCOME_VRAI
    assert m.outcome != jr.OUTCOME_MARCHE_FERME


@requires_lib
def test_or_continu_7j_juneteenth_mesure_normalement(tmp_path, _suivi_override):
    """Or (continu) un férié US : cote en continu → mesuré normalement."""
    m = _measure_7j(
        tmp_path, FICHE_OR, "or", "GC=F", "Or", close=104.0,
    )
    # 100 → 104 = +4 % > seuil 1.3 %, LONG → VRAI. Surtout PAS marche-ferme.
    assert m.outcome == jr.OUTCOME_VRAI
    assert m.outcome != jr.OUTCOME_MARCHE_FERME


def test_or_continu_7j_jour_ouvre_normal_non_skippe(tmp_path, _suivi_override):
    """Contre-épreuve hors lib : un continu un jour OUVRÉ normal n'est jamais
    skippé (échéance 7j = jour ouvré → mesuré). Garantit zéro régression sur le
    chemin nominal même sans la lib `holidays`."""
    bdate = date(2026, 6, 2)  # echeance 7j = 09/06 (mardi ordinaire, ouvert partout)
    assert jr.compute_echeance(bdate, "7j") == date(2026, 6, 9)
    bulletins = tmp_path / "bulletins"
    prix_emis = tmp_path / "prix-emission"
    prix_ouv = tmp_path / "prix-ouverture"
    bulletins.mkdir()
    (bulletins / f"bulletin-{bdate.isoformat()}-07h.md").write_text(
        f"# Bulletin — {bdate.isoformat()}\n\n## Matrice\n\n"
        "| Actif | 24h | 7j | 1m |\n|---|---|---|---|\n"
        "| Or | LONG (+2.0) | LONG (+2.0) | LONG (+2.0) |\n",
        encoding="utf-8",
    )
    prix_emis.mkdir()
    (prix_emis / f"{bdate.isoformat()}-07h.json").write_text(json.dumps({"GC=F": 100.0}))
    prix_ouv.mkdir()
    (prix_ouv / f"{bdate.isoformat()}.json").write_text(json.dumps({"GC=F": 100.0}))
    measures, _ = jr.measure(
        today=date(2026, 6, 9), bulletins_dir=bulletins, prix_emission_dir=prix_emis,
        prix_ouverture_dir=prix_ouv, fiches={"or": FICHE_OR},
        fetch_price=lambda t: 104.0,
    )
    m = [mm for mm in measures if mm.horizon == "7j"][0]
    assert m.outcome == jr.OUTCOME_VRAI
    assert m.outcome != jr.OUTCOME_MARCHE_FERME
