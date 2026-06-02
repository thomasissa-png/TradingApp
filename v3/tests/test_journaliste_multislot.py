"""Tests multi-créneaux (3 bulletins/jour : matin/midi/soir).

Contexte : il y a 3 runs/jour (cron UTC 5/10/16). Avant le correctif, ils
écrivaient TOUS dans bulletin-{date}.md → chaque run écrasait le précédent
(seul le soir survivait). Désormais chaque créneau a son fichier
bulletin-{date}-{HH}h.md et SES propres prix d'émission (clés par identité
de bulletin = stem, pas par date).

Ces tests verrouillent :
  1. Le nouveau nommage est parsé, l'identité (bulletin_id) inclut le créneau.
  2. Rétro-compat : l'ancien nommage bulletin-{date}.md reste mesuré.
  3. Prix d'émission clés par identité de bulletin (pas par date) → 2 créneaux
     du même jour ont des prix distincts.
  4. Deux bulletins le même jour sont mesurés INDÉPENDAMMENT (pas fusionnés)
     avec des prix d'émission distincts → outcomes potentiellement différents.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import journaliste as jr  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_bulletin(dir_: Path, filename: str, d: date, rows: List[tuple]) -> Path:
    """Écrit un bulletin minimal avec un nom de fichier arbitraire."""
    dir_.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Bulletin Analyste — {d.isoformat()}",
        "",
        "| Actif | 24h | 7j | 1m |",
        "|---|---|---|---|",
    ]
    for actif, (c24, s24), (c7, s7), (c1, s1) in rows:
        lines.append(
            f"| {actif} | {c24} ({s24:+.2f}) | {c7} ({s7:+.2f}) | {c1} ({s1:+.2f}) |"
        )
    path = dir_ / filename
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _fiche_petrole() -> dict:
    return {
        "actif": "Pétrole (Brent)",
        "ticker_principal": "BZ=F",
        "seuils_reussite_pct": {"24h": 1.0, "7j": 2.5, "1m": 6.0},
    }


# ---------------------------------------------------------------------------
# Parsing du nouveau nommage + identité
# ---------------------------------------------------------------------------

def test_parse_nouveau_nommage_creneau(tmp_path):
    d = date(2026, 6, 2)
    p = _write_bulletin(
        tmp_path, "bulletin-2026-06-02-16h.md", d,
        [("Pétrole (Brent)", ("LONG", 0.4), ("SHORT", -1.0), ("LONG", 2.0))],
    )
    cells = jr.parse_bulletin(p)
    assert len(cells) == 3
    # La date est bien extraite, l'identité inclut le créneau.
    assert all(c.bulletin_date == d for c in cells)
    assert all(c.bulletin_id == "2026-06-02-16h" for c in cells)


def test_parse_ancien_nommage_retrocompat(tmp_path):
    d = date(2026, 6, 2)
    p = _write_bulletin(
        tmp_path, "bulletin-2026-06-02.md", d,
        [("Pétrole (Brent)", ("LONG", 0.4), ("SHORT", -1.0), ("LONG", 2.0))],
    )
    cells = jr.parse_bulletin(p)
    assert len(cells) == 3
    assert all(c.bulletin_date == d for c in cells)
    # Pas de créneau → identité = date seule (rétro-compat).
    assert all(c.bulletin_id == "2026-06-02" for c in cells)


def test_bulletin_id_from_path():
    assert jr.bulletin_id_from_path(Path("bulletin-2026-06-02-05h.md")) == "2026-06-02-05h"
    assert jr.bulletin_id_from_path(Path("bulletin-2026-06-02.md")) == "2026-06-02"
    assert jr.bulletin_id_from_path(Path("autre.md")) is None


# ---------------------------------------------------------------------------
# Prix d'émission clés par identité de bulletin (pas par date)
# ---------------------------------------------------------------------------

def test_prix_emission_clef_par_creneau(tmp_path):
    """2 créneaux du même jour → 2 fichiers de prix distincts, pas de collision."""
    base = tmp_path / "prix-emission"
    matin = "2026-06-02-05h"
    soir = "2026-06-02-16h"
    jr.stamp_prix_emission(
        matin, fiches={"petrole": _fiche_petrole()},
        fetch_price=lambda t: 100.0, base_dir=base,
    )
    jr.stamp_prix_emission(
        soir, fiches={"petrole": _fiche_petrole()},
        fetch_price=lambda t: 110.0, base_dir=base,
    )
    # Deux fichiers distincts.
    assert (base / "2026-06-02-05h.json").exists()
    assert (base / "2026-06-02-16h.json").exists()
    # Prix d'émission distincts par créneau (pas écrasés).
    assert jr.load_prix_emission(matin, base) == {"BZ=F": 100.0}
    assert jr.load_prix_emission(soir, base) == {"BZ=F": 110.0}


def test_prix_emission_retrocompat_date(tmp_path):
    """Passer un `date` continue d'écrire prix-emission/{date}.json (rétro-compat)."""
    base = tmp_path / "prix-emission"
    d = date(2026, 6, 2)
    jr.stamp_prix_emission(
        d, fiches={"petrole": _fiche_petrole()},
        fetch_price=lambda t: 100.0, base_dir=base,
    )
    assert (base / "2026-06-02.json").exists()
    assert jr.load_prix_emission(d, base) == {"BZ=F": 100.0}


# ---------------------------------------------------------------------------
# Mesure indépendante de 2 bulletins le même jour
# ---------------------------------------------------------------------------

def test_deux_bulletins_meme_jour_mesures_independamment(tmp_path):
    """Matin et soir le 2026-06-02, prix d'émission distincts → mesurés chacun
    contre SES prix. Avec prix d'émission différents, un même prix courant donne
    des deltas différents → les deux jeux de prédictions sont indépendants."""
    bulletins_dir = tmp_path / "bulletins"
    prix_dir = tmp_path / "prix-emission"
    d = date(2026, 6, 2)
    today = date(2026, 6, 4)  # 24h et 7j peuvent être échus pour 24h

    # Même cellule (Pétrole LONG 24h) dans les deux créneaux.
    _write_bulletin(
        bulletins_dir, "bulletin-2026-06-02-05h.md", d,
        [("Pétrole (Brent)", ("LONG", 0.4), ("SHORT", -1.0), ("LONG", 2.0))],
    )
    _write_bulletin(
        bulletins_dir, "bulletin-2026-06-02-16h.md", d,
        [("Pétrole (Brent)", ("LONG", 0.4), ("SHORT", -1.0), ("LONG", 2.0))],
    )

    # Prix d'émission DISTINCTS par créneau.
    prix_dir.mkdir(parents=True, exist_ok=True)
    (prix_dir / "2026-06-02-05h.json").write_text(
        json.dumps({"BZ=F": 100.0}), encoding="utf-8"
    )
    (prix_dir / "2026-06-02-16h.json").write_text(
        json.dumps({"BZ=F": 103.0}), encoding="utf-8"
    )

    fiches = {"petrole": _fiche_petrole()}
    # Prix courant unique pour le run.
    measures, _kpis = jr.measure(
        today=today,
        bulletins_dir=bulletins_dir,
        prix_emission_dir=prix_dir,
        fiches=fiches,
        fetch_price=lambda t: 102.0,  # prix courant
    )

    # Mesures du créneau 24h pour chaque bulletin.
    m24 = [m for m in measures if m.horizon == "24h"]
    by_id = {m.cell.bulletin_id: m for m in m24}
    assert "2026-06-02-05h" in by_id
    assert "2026-06-02-16h" in by_id
    # NON fusionnés : 2 mesures distinctes, prix d'émission propres à chacun.
    assert by_id["2026-06-02-05h"].prix_emission == 100.0
    assert by_id["2026-06-02-16h"].prix_emission == 103.0
    # Matin : 100 → 102 = +2 % (LONG, seuil 1 %) → VRAI.
    assert by_id["2026-06-02-05h"].outcome == jr.OUTCOME_VRAI
    # Soir : 103 → 102 = -0.97 % (LONG, seuil 1 %) → non-conclusive (< seuil).
    assert by_id["2026-06-02-16h"].outcome == jr.OUTCOME_NC


def test_run_journaliste_stamp_creneau_le_plus_recent(tmp_path):
    """journaliste.run(stamp_today=True) stampe l'identité du bulletin le plus
    récent du jour (le soir), pas la date seule."""
    bulletins_dir = tmp_path / "bulletins"
    prix_dir = tmp_path / "prix-emission"
    perf = tmp_path / "performance.md"
    today = date(2026, 6, 2)

    _write_bulletin(
        bulletins_dir, "bulletin-2026-06-02-05h.md", today,
        [("Pétrole (Brent)", ("LONG", 0.4), ("SHORT", -1.0), ("LONG", 2.0))],
    )
    _write_bulletin(
        bulletins_dir, "bulletin-2026-06-02-16h.md", today,
        [("Pétrole (Brent)", ("LONG", 0.4), ("SHORT", -1.0), ("LONG", 2.0))],
    )

    jr.run(
        today=today,
        bulletins_dir=bulletins_dir,
        prix_emission_dir=prix_dir,
        performance_path=perf,
        fiches={"petrole": _fiche_petrole()},
        fetch_price=lambda t: 100.0,
        stamp_today=True,
    )
    # Stamp clé sur le créneau le plus récent du jour (soir), pas sur "2026-06-02".
    assert (prix_dir / "2026-06-02-16h.json").exists()
    assert not (prix_dir / "2026-06-02.json").exists()
