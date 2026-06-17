"""TEST-VERROU L027 — la fenêtre de mesure des continus ne tronque plus le mouvement.

Critère d'acceptation n°1 du fix L027 (GO mesure Thomas, 16/06) :

  Le 15/06, l'or (continu, SHORT 24h) a fait, vu de la session :
    open ≈ 4215 → close ≈ 4309  (+2,2 %, plus haut +3,6 %)
  Le call SHORT était PERDANT. Mais le système l'a classé « NC » (+0,18 %)
  car sa référence d'« ouverture » stampée à 8h Paris (≈ 4308) tombait APRÈS
  le rallye depuis l'émission 7h → le 24h n'était mesuré que sur les derniers
  +0,18 %, sous le seuil 0,5 % → NC. Conséquence : le win rate des continus
  CACHAIT des pertes.

Après le fix (référence continus = prix d'ÉMISSION 7h, point d'exécution réel),
ce même call doit ressortir **FAUX** (FAUSSE), plus jamais « NC ».

WIN RATE ONLY : l'amplitude % ne sert qu'à seuiller VRAI/FAUX/NC, aucun montant.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import journaliste as jr  # noqa: E402

# Fiche or RÉELLE : continu, seuil 24h = 0,5 % (cf. config/fiches/or.yml).
FICHE_OR = {
    "actif": "Or",
    "ticker_principal": "GC=F",
    "famille": "métaux-précieux",
    "seuils_reussite_pct": {"24h": 0.5, "7j": 1.3, "1m": 3.0},
}

# Chiffres du cas fondateur (XAU/USD natif, session du 15/06).
EMISSION_7H = 4215.0   # prix lu/actionnable à l'émission 7h (open de session)
OUVERTURE_8H = 4308.0  # ancienne « ouverture » stampée à 8h — APRÈS le rallye
CLOSE = 4309.0         # clôture 24h


def _write_bulletin_7h_short_or(bulletins_dir: Path, bdate: date) -> Path:
    bulletins_dir.mkdir(parents=True, exist_ok=True)
    p = bulletins_dir / f"bulletin-{bdate.isoformat()}-07h.md"
    p.write_text(
        f"# Bulletin — {bdate.isoformat()}\n\n## Matrice\n\n"
        "| Actif | 24h | 7j | 1m |\n|---|---|---|---|\n"
        "| Or | SHORT (-1.5) | SHORT (-1.5) | SHORT (-1.5) |\n",
        encoding="utf-8",
    )
    return p


def _measure_or_24h(tmp_path, *, emission, ouverture, close):
    bdate = date(2026, 6, 15)
    today = jr.compute_echeance(bdate, "24h")
    bulletins = tmp_path / "bulletins"
    prix_emis = tmp_path / "prix-emission"
    prix_ouv = tmp_path / "prix-ouverture"
    _write_bulletin_7h_short_or(bulletins, bdate)
    prix_emis.mkdir()
    (prix_emis / f"{bdate.isoformat()}-07h.json").write_text(
        json.dumps({"GC=F": emission})
    )
    prix_ouv.mkdir()
    (prix_ouv / f"{bdate.isoformat()}.json").write_text(
        json.dumps({"GC=F": ouverture})
    )
    measures, _ = jr.measure(
        today=today, bulletins_dir=bulletins, prix_emission_dir=prix_emis,
        prix_ouverture_dir=prix_ouv, fiches={"or": FICHE_OR},
        fetch_price=lambda t: close,
    )
    return [m for m in measures if m.horizon == "24h"][0]


def test_verrou_or_15_06_short_ressort_FAUX_pas_NC(tmp_path):
    """CRITÈRE D'ACCEPTATION N°1 : le SHORT or du 15/06 ressort FAUX, plus NC."""
    m = _measure_or_24h(
        tmp_path, emission=EMISSION_7H, ouverture=OUVERTURE_8H, close=CLOSE,
    )
    # Référence = ÉMISSION 7h (point d'exécution réel), PAS l'ouverture 8h.
    assert m.prix_reference_source == "emission"
    assert m.prix_emission == EMISSION_7H
    # 4215 → 4309 = +2,23 % > seuil 0,5 %, SHORT → mouvement CONTRE le call.
    assert m.outcome == jr.OUTCOME_FAUSSE
    assert m.outcome != jr.OUTCOME_NC  # explicite : plus jamais « non-conclusive »
    assert m.delta_pct is not None and m.delta_pct > 0.5


def test_verrou_demontre_le_bug_avec_ancienne_reference_8h(tmp_path):
    """Contre-épreuve : avec l'ANCIENNE référence 8h (=ouverture), le même call
    serait classé NC — c'est exactement le bug que le fix corrige.

    On force ici la mesure depuis l'ouverture 8h en rendant l'émission absente
    (le fallback continu retombe alors sur l'ouverture) pour matérialiser, dans
    le test, l'écart de verdict entre les deux références.
    """
    m_bug = _measure_or_24h(
        tmp_path, emission=None, ouverture=OUVERTURE_8H, close=CLOSE,
    )
    # Référence dégradée = ouverture 8h (émission absente).
    assert m_bug.prix_reference_source == "ouverture"
    assert m_bug.prix_emission == OUVERTURE_8H
    # 4308 → 4309 = +0,02 % ≤ seuil 0,5 % → NC (le mouvement réel est masqué).
    assert m_bug.outcome == jr.OUTCOME_NC


def test_verrou_emission_None_dict(tmp_path):
    """Garde-fou : un émission présent dans le dict mais à None ne casse pas la
    résolution (continu retombe sur l'ouverture, zéro plantage)."""
    bdate = date(2026, 6, 15)
    today = jr.compute_echeance(bdate, "24h")
    bulletins = tmp_path / "bulletins"
    prix_emis = tmp_path / "prix-emission"
    prix_ouv = tmp_path / "prix-ouverture"
    _write_bulletin_7h_short_or(bulletins, bdate)
    prix_emis.mkdir()
    (prix_emis / f"{bdate.isoformat()}-07h.json").write_text(json.dumps({}))
    prix_ouv.mkdir()
    (prix_ouv / f"{bdate.isoformat()}.json").write_text(json.dumps({"GC=F": OUVERTURE_8H}))
    measures, _ = jr.measure(
        today=today, bulletins_dir=bulletins, prix_emission_dir=prix_emis,
        prix_ouverture_dir=prix_ouv, fiches={"or": FICHE_OR},
        fetch_price=lambda t: CLOSE,
    )
    m = [mm for mm in measures if mm.horizon == "24h"][0]
    assert m.prix_reference_source == "ouverture"
