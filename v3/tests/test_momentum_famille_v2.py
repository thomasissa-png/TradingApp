"""Tests momentum-prix v3 — vague 2 (A3 poids ≤6 + A8/A9 famille).

Audit momentum-family 10/06 (`v3/audit/momentum-family-verdict.md`) :
  A3 — poids momentum CONSERVATEURS ≤ 6 (prove-first) sur TOUTES les fiches.
  A8 — fin de la famille : EUR/USD + indices (S&P 500/Nasdaq/CAC 40), indices
       plafonnés à 4-5, RSI poids 2 CONSERVÉ.
  A9 — VIX EXCLU du momentum (mean-reverting).

Garde-fous anti-régression : les 4 nouvelles clés existent dans TWELVE_SYMBOLS
ET dans les YAML, aucun `momentum_prix_*` ne dépasse 6, VIX n'a aucun momentum.
"""

from __future__ import annotations

import criteres_calculator as cc


def _momentum_criteres():
    """Liste (stem, critère) de tous les critères momentum_prix_* des fiches."""
    fiches = cc.load_fiches()
    out = []
    for stem, fiche in fiches.items():
        for c in fiche.get("criteres", []):
            cle = c.get("cle_courante", "") or ""
            if cle.startswith("momentum_prix_"):
                out.append((stem, c))
    return out


# --------------------------------------------------------------------------
# A3 — poids ≤ 6 partout (prove-first)
# --------------------------------------------------------------------------

def test_a3_tous_les_momentum_poids_inferieur_ou_egal_6():
    """Aucun critère momentum_prix_* ne dépasse 6 (plafond prove-first A3)."""
    crits = _momentum_criteres()
    assert crits, "Aucun critère momentum trouvé — chargement des fiches cassé ?"
    for stem, c in crits:
        poids = c.get("poids")
        assert isinstance(poids, int), f"{stem}: poids momentum non entier ({poids!r})"
        assert poids <= 6, f"{stem}: poids momentum {poids} > 6 (viole A3 prove-first)"


def test_a3_poids_attendus_par_fiche():
    """Poids EXACTS attendus après la vague 2 (cacao 9→6, indices 4, eurusd 5...)."""
    attendus = {
        "cacao": 6, "cafe": 6, "ble": 6, "cuivre": 6,
        "petrole": 6, "or": 6, "argent": 6,
        "eurusd": 5,
        "sp500": 4, "nasdaq": 4, "cac40": 4,
    }
    fiches = cc.load_fiches()
    for stem, poids_attendu in attendus.items():
        crit = next(
            (c for c in fiches[stem].get("criteres", [])
             if (c.get("cle_courante") or "").startswith("momentum_prix_")),
            None,
        )
        assert crit is not None, f"{stem}: critère momentum absent"
        assert crit["poids"] == poids_attendu, (
            f"{stem}: poids momentum {crit['poids']} != {poids_attendu} attendu"
        )


# --------------------------------------------------------------------------
# A8 — les 4 nouvelles clés existent dans TWELVE_SYMBOLS ∩ YAML, mapping cohérent
# --------------------------------------------------------------------------

def test_a8_nouvelles_cles_dans_twelve_symbols():
    """Les 4 clés vague 2 sont mappées dans TWELVE_SYMBOLS (sinon n/a silencieux)."""
    attendu = {
        "momentum_prix_20j_eurusd": "EUR=X",
        "momentum_prix_20j_sp500": "SPY",
        "momentum_prix_20j_nasdaq": "QQQ",
        "momentum_prix_20j_cac40": "^FCHI",
    }
    for cle, symbole in attendu.items():
        assert cle in cc.TWELVE_SYMBOLS, f"{cle} absent de TWELVE_SYMBOLS"
        assert cc.TWELVE_SYMBOLS[cle] == symbole, (
            f"{cle} → {cc.TWELVE_SYMBOLS[cle]} != {symbole} attendu"
        )


def test_a8_chaque_cle_yaml_momentum_est_mappee():
    """Toute clé momentum_prix_* d'une fiche DOIT être dans TWELVE_SYMBOLS.

    Sinon le critère tomberait en n/a silencieux (pas de symbole à fetcher).
    """
    for stem, c in _momentum_criteres():
        cle = c["cle_courante"]
        assert cle in cc.TWELVE_SYMBOLS, (
            f"{stem}: {cle} absent de TWELVE_SYMBOLS (n/a silencieux)"
        )


def test_a8_indices_rsi_poids_2_conserve():
    """A8 : RSI des indices CONSERVÉ à poids 2 (le momentum ne le remplace pas)."""
    fiches = cc.load_fiches()
    rsi_cles = {
        "sp500": "rsi_14j_gspc",
        "nasdaq": "rsi_14j_ixic",
        "cac40": "rsi_14j_fchi",
    }
    for stem, rsi_cle in rsi_cles.items():
        crit = next(
            (c for c in fiches[stem]["criteres"] if c.get("cle_courante") == rsi_cle),
            None,
        )
        assert crit is not None, f"{stem}: RSI {rsi_cle} introuvable"
        assert crit["poids"] == 2, f"{stem}: RSI poids {crit['poids']} != 2 (A8 viole)"


def test_a8_signe_plus_un_partout():
    """Tous les momentum suivent la tendance (signe +1), jamais contrarian."""
    for stem, c in _momentum_criteres():
        assert c.get("signe") == 1, f"{stem}: momentum signe {c.get('signe')} != +1"


# --------------------------------------------------------------------------
# A9 — VIX EXCLU du momentum (mean-reverting)
# --------------------------------------------------------------------------

def test_a9_vix_sans_momentum():
    """A9 (unanime) : la fiche VIX ne contient AUCUN critère momentum_prix_*."""
    fiches = cc.load_fiches()
    assert "vix" in fiches, "fiche vix introuvable"
    cles = {(c.get("cle_courante") or "") for c in fiches["vix"]["criteres"]}
    assert not any(k.startswith("momentum_prix_") for k in cles), (
        "VIX ne doit avoir aucun momentum (mean-reverting, A9)"
    )
    # Garde-fou aussi côté TWELVE_SYMBOLS : pas de clé momentum vix.
    assert "momentum_prix_20j_vix" not in cc.TWELVE_SYMBOLS


def test_famille_complete_14_actifs():
    """La famille couvre exactement 14 actifs (15 fiches - VIX exclu).

    MAJ 2026-06-26 : ajout de usdjpy / coton / sucre (nouveaux actifs, momentum
    7j/20j câblé). VIX reste exclu (mean-reverting, A9). Passé de 11 à 14.
    """
    crits = _momentum_criteres()
    stems = {stem for stem, _ in crits}
    attendus = {
        "cacao", "cafe", "ble", "cuivre", "petrole", "or", "argent",
        "eurusd", "sp500", "nasdaq", "cac40",
        "usdjpy", "coton", "sucre",
    }
    assert stems == attendus, f"Famille momentum: {stems} != {attendus}"
    assert "vix" not in stems
