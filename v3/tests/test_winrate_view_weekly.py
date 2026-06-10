"""Tests — vue WIN RATE propre + archive hebdomadaire figée (Session 4).

Refonte de `performance.md` :
- tableau win-rate-only (zéro P&L), groupé par horizon, trié par win rate
  décroissant, 36 cellules (12 actifs × 3 horizons) toujours visibles dont 1m ;
- archive hebdo `v3/data/performance/weekly/win-rate-{ISO}.md` (un fichier par
  semaine ISO, réécrit pendant la semaine puis figé).

La logique de mesure (compute_kpi, seuils VRAI/FAUX, N_eff) n'est PAS testée ici
(inchangée) — on teste la PRÉSENTATION + l'archive.
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List
from zoneinfo import ZoneInfo

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import journaliste as jr  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# 12 actifs (clé fiche → nom affiché) pour reproduire les 36 cellules réelles.
FICHES: Dict[str, dict] = {
    "argent": {"actif": "Argent", "ticker_principal": "SI=F"},
    "ble": {"actif": "Blé", "ticker_principal": "ZW=F"},
    "cac40": {"actif": "CAC 40", "ticker_principal": "^FCHI"},
    "cacao": {"actif": "Cacao", "ticker_principal": "CC=F"},
    "cafe": {"actif": "Café (Arabica)", "ticker_principal": "KC=F"},
    "cuivre": {"actif": "Cuivre", "ticker_principal": "HG=F"},
    "eurusd": {"actif": "EUR/USD", "ticker_principal": "EURUSD"},
    "nasdaq": {"actif": "Nasdaq", "ticker_principal": "QQQ"},
    "or": {"actif": "Or", "ticker_principal": "XAU/USD"},
    "petrole": {"actif": "Pétrole (Brent)", "ticker_principal": "BZ=F"},
    "sp500": {"actif": "S&P 500", "ticker_principal": "SPY"},
    "vix": {"actif": "VIX", "ticker_principal": "VIXY"},
}


def _measure(fiche_key: str, actif: str, outcome: str, echeance: date,
             horizon: str = "24h", conc: str = "LONG", is_flip=None) -> jr.Measure:
    cell = jr.BulletinCell(
        bulletin_date=echeance - timedelta(days=jr.HORIZON_DAYS[horizon]),
        actif_name=actif,
        horizon=horizon,
        conclusion=conc,
        score=2.0,
    )
    return jr.Measure(
        cell=cell, fiche_key=fiche_key, ticker="", horizon=horizon,
        echeance=echeance, prix_emission=100.0, prix_courant=101.0,
        seuil_pct=1.0, delta_pct=1.0, outcome=outcome, is_flip=is_flip,
    )


def _kpis_from(measures: List[jr.Measure]) -> Dict:
    by_cell: Dict = {}
    for m in measures:
        by_cell.setdefault((m.fiche_key, m.horizon), []).append(m)
    for k in by_cell:
        by_cell[k].sort(key=lambda m: m.echeance)
    return {k: jr.compute_kpi(v) for k, v in by_cell.items()}


NOW = datetime(2026, 6, 8, 7, 5, tzinfo=ZoneInfo("Europe/Paris"))


# ---------------------------------------------------------------------------
# Tableau win-rate propre (render_performance)
# ---------------------------------------------------------------------------

def test_table_colonnes_win_rate_only():
    """En-tête exact : Actif | Win rate | WR tradable | Paris (réels) | Non notés | Statut.

    Le WR tradable COEXISTE avec le WR conclusif (Lot 2 audit 10/06) : la colonne
    s'ajoute à côté, rien n'est retiré.
    """
    ms = [_measure("petrole", "Pétrole (Brent)", jr.OUTCOME_VRAI, date(2026, 6, 1))]
    out = jr.render_performance(_kpis_from(ms), ms, NOW, fiches=FICHES)
    assert "| Actif | Win rate | WR tradable | Paris (réels) | Non notés | Statut |" in out


def test_table_zero_argent_et_jargon_retire():
    """Aucune notion d'argent ; Brier / Taux_brut / Alertes retirés de la vue."""
    ms = [_measure("or", "Or", jr.OUTCOME_VRAI, date(2026, 6, 1))]
    out = jr.render_performance(_kpis_from(ms), ms, NOW, fiches=FICHES)
    for banned in ["Brier", "Taux_brut", "| Alertes", "P&L", "€", "$",
                   "gain", "Wilson_low", "LONG/SHORT"]:
        assert banned not in out, f"Terme interdit affiché : {banned}"


def test_table_36_lignes_dont_1m_visibles():
    """Les 36 cellules (12 actifs × 3 horizons) sont présentes, dont le 1m vide."""
    ms = [_measure("petrole", "Pétrole (Brent)", jr.OUTCOME_VRAI, date(2026, 6, 1))]
    out = jr.render_performance(_kpis_from(ms), ms, NOW, fiches=FICHES)
    # 3 groupes d'horizon
    for label in ("### 24 heures", "### 7 jours", "### 1 mois"):
        assert label in out, f"Groupe d'horizon manquant : {label}"
    # Le 1m est en attente pour tous (aucune mesure 1m fournie)
    bloc_1m = out.split("### 1 mois")[1]
    assert bloc_1m.count("⏳ en attente") == 12
    # Total de lignes de données (hors en-têtes/séparateurs) = 36
    data_rows = [
        l for l in out.splitlines()
        if l.startswith("| ") and "Actif" not in l and set(l) - set("|-: ")
    ]
    assert len(data_rows) == 36, f"Attendu 36 lignes, obtenu {len(data_rows)}"


def test_table_tri_win_rate_decroissant_dans_groupe():
    """Dans le groupe 24h, les win rates sont triés en ordre décroissant."""
    base = date(2026, 6, 1)
    ms = [
        _measure("petrole", "Pétrole (Brent)", jr.OUTCOME_FAUSSE, base),  # 0 %
        _measure("or", "Or", jr.OUTCOME_VRAI, base),                       # 100 %
        _measure("argent", "Argent", jr.OUTCOME_VRAI, base + timedelta(days=2)),
        _measure("argent", "Argent", jr.OUTCOME_FAUSSE, base + timedelta(days=4)),  # 50 %
    ]
    out = jr.render_performance(_kpis_from(ms), ms, NOW, fiches=FICHES)
    bloc_24h = out.split("### 24 heures")[1].split("###")[0]
    # Or (100 %) avant Argent (50 %) avant Pétrole (0 %)
    assert bloc_24h.index("| Or ") < bloc_24h.index("| Argent ")
    assert bloc_24h.index("| Argent ") < bloc_24h.index("| Pétrole (Brent) ")


def test_table_statuts_win_rate_only():
    """Statuts : trop peu / en attente (et objectif/sous-objectif au seuil)."""
    # 1 mesure 24h → trop peu (1/15) ; pas de mesure 1m → en attente.
    ms = [_measure("vix", "VIX", jr.OUTCOME_VRAI, date(2026, 6, 1))]
    out = jr.render_performance(_kpis_from(ms), ms, NOW, fiches=FICHES)
    assert "⏳ trop peu (1/15)" in out
    assert "⏳ en attente" in out


def test_statut_objectif_atteint_si_n_eff_suffisant():
    """N_eff ≥ 15, win rate 100 %, Wilson_low > 50 % → ✅ objectif atteint."""
    base = date(2026, 1, 1)
    ms = [
        _measure("petrole", "Pétrole (Brent)", jr.OUTCOME_VRAI,
                 base + timedelta(days=2 * i))
        for i in range(20)
    ]
    kpis = _kpis_from(ms)
    out = jr.render_performance(kpis, ms, NOW, fiches=FICHES)
    assert "✅ objectif atteint" in out


def test_statut_sous_objectif_si_taux_insuffisant():
    """N_eff ≥ 15 mais win rate trop bas → ❌ sous l'objectif."""
    base = date(2026, 1, 1)
    outcomes = [jr.OUTCOME_VRAI, jr.OUTCOME_FAUSSE] * 10  # ~50 %
    ms = [
        _measure("cacao", "Cacao", o, base + timedelta(days=2 * i))
        for i, o in enumerate(outcomes)
    ]
    out = jr.render_performance(_kpis_from(ms), ms, NOW, fiches=FICHES)
    assert "❌ sous l'objectif" in out


def test_table_synthese_ligne_en_haut():
    """Ligne de synthèse « X / 36 cellules fiables » présente, avec message
    de chauffe si X = 0."""
    ms = [_measure("or", "Or", jr.OUTCOME_VRAI, date(2026, 6, 1))]
    out = jr.render_performance(_kpis_from(ms), ms, NOW, fiches=FICHES)
    assert "0 / 36 cellules fiables" in out
    assert "Tout est en chauffe" in out


# ---------------------------------------------------------------------------
# Semaine ISO
# ---------------------------------------------------------------------------

def test_iso_week_label_format():
    assert jr.iso_week_label(NOW) == "2026-S24"


def test_iso_week_bounds_lundi_dimanche():
    monday, sunday = jr.iso_week_bounds(NOW)
    assert monday == date(2026, 6, 8)   # lundi
    assert sunday == date(2026, 6, 14)  # dimanche
    assert (sunday - monday).days == 6


# ---------------------------------------------------------------------------
# Archive hebdomadaire figée
# ---------------------------------------------------------------------------

def test_weekly_fichier_cree_au_bon_chemin(tmp_path):
    """write_weekly_winrate écrit win-rate-{ISO}.md dans le dossier weekly."""
    content = jr.render_weekly_winrate(
        _kpis_from([_measure("or", "Or", jr.OUTCOME_VRAI, date(2026, 6, 1))]),
        [], NOW, fiches=FICHES,
    )
    weekly_dir = tmp_path / "weekly"
    path = jr.write_weekly_winrate(content, NOW, weekly_dir=weekly_dir)
    assert path == weekly_dir / "win-rate-2026-S24.md"
    assert path.exists()


def test_weekly_contenu_tableau_et_colonne_nouveaux_paris():
    """L'archive contient l'en-tête semaine, le tableau et la colonne
    « Nouveaux paris (semaine) »."""
    base = date(2026, 6, 8)  # dans la semaine ISO S24
    ms = [
        _measure("or", "Or", jr.OUTCOME_VRAI, base),
        _measure("or", "Or", jr.OUTCOME_VRAI, base + timedelta(days=2)),
    ]
    out = jr.render_weekly_winrate(_kpis_from(ms), ms, NOW, fiches=FICHES)
    assert "# Win rate — semaine 2026-S24 (2026-06-08 → 2026-06-14)" in out
    assert "Nouveaux paris (semaine)" in out
    # 2 mesures Or 24h échues dans la semaine → 2 nouveaux paris.
    bloc_24h = out.split("### 24 heures")[1].split("###")[0]
    ligne_or = next(l for l in bloc_24h.splitlines() if l.startswith("| Or "))
    # Colonnes : Actif | Win rate | WR tradable | Paris | Nouveaux | Non notés | Statut
    # (WR tradable inséré en index 3 → « Nouveaux paris » passe de l'index 4 à 5).
    assert ligne_or.split("|")[5].strip() == "2"


def test_weekly_nouveaux_paris_zero_hors_semaine():
    """Une mesure échue HORS de la semaine ISO ne compte pas comme nouvelle."""
    hors = date(2026, 5, 15)  # bien avant la semaine S24
    ms = [_measure("or", "Or", jr.OUTCOME_VRAI, hors)]
    out = jr.render_weekly_winrate(_kpis_from(ms), ms, NOW, fiches=FICHES)
    bloc_24h = out.split("### 24 heures")[1].split("###")[0]
    ligne_or = next(l for l in bloc_24h.splitlines() if l.startswith("| Or "))
    # « Nouveaux paris » en index 5 (WR tradable inséré en index 3).
    assert ligne_or.split("|")[5].strip() == "0"


def test_weekly_zero_argent():
    """L'archive hebdo est aussi win-rate-only (zéro P&L)."""
    ms = [_measure("or", "Or", jr.OUTCOME_VRAI, date(2026, 6, 8))]
    out = jr.render_weekly_winrate(_kpis_from(ms), ms, NOW, fiches=FICHES)
    for banned in ["Brier", "P&L", "€", "$", "gain"]:
        assert banned not in out, f"Terme interdit affiché : {banned}"


# ---------------------------------------------------------------------------
# Bout-en-bout : run() écrit l'archive hebdo
# ---------------------------------------------------------------------------

def _write_bulletin(bulletins: Path, d: date, actif: str, horizon_concs) -> None:
    bulletins.mkdir(parents=True, exist_ok=True)
    lines = [f"# Bulletin Analyste — {d.isoformat()}", "", "## Synthèse des décisions",
             "", "| Actif | 24h | 7j | 1m |", "|---|---|---|---|"]
    c24, c7, c1 = horizon_concs
    lines.append(f"| {actif} | {c24} | {c7} | {c1} |")
    (bulletins / f"bulletin-{d.isoformat()}.md").write_text("\n".join(lines), encoding="utf-8")


def test_run_ecrit_archive_hebdo(tmp_path):
    """run() crée v3/data/performance/weekly/win-rate-{ISO}.md."""
    bulletins = tmp_path / "bulletins"
    prix = tmp_path / "prix-emission"
    perf = tmp_path / "performance.md"
    d_em = date(2026, 6, 5)
    today = date(2026, 6, 8)
    _write_bulletin(bulletins, d_em, "Pétrole (Brent)", ("LONG -0.5", "SHORT", "LONG"))
    prix.mkdir(parents=True, exist_ok=True)
    (prix / f"{d_em.isoformat()}.json").write_text('{"BZ=F": 100.0}', encoding="utf-8")
    now = datetime(2026, 6, 8, 7, 0, tzinfo=ZoneInfo("Europe/Paris"))

    jr.run(
        today=today, now=now,
        bulletins_dir=bulletins, prix_emission_dir=prix, performance_path=perf,
        fiches={"petrole": FICHES["petrole"]},
        fetch_price=lambda t: 105.0, stamp_today=False,
    )
    weekly_path = perf.parent / "performance" / "weekly" / "win-rate-2026-S24.md"
    assert weekly_path.exists()
    content = weekly_path.read_text(encoding="utf-8")
    assert "# Win rate — semaine 2026-S24" in content
    assert "Nouveaux paris (semaine)" in content
