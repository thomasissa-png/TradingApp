"""Tests wording des noms de critères dans les fiches (config/fiches/*.yml).

Garantit que les acronymes de sources techniques (NOAA, WASDE, COT, COMEX, LME,
SHFE, EIA, DXY, GATE…) ont été retirés des libellés `nom:` affichés à l'humain,
suite à la reformulation en langage trader (reco-wording-noms-criteres.md).

Les acronymes PORTEURS D'INFO conservés volontairement (PMI, RSI, VIX/VXN/V2X,
SKEW/VVIX, ICE, CAPE) ne sont PAS interdits — ils sont couverts par le glossaire.

Ne touche QUE le champ `nom:` ; les `cle_courante`, `source`, poids, etc. sont
hors périmètre (et peuvent légitimement contenir ces acronymes).
"""

from __future__ import annotations

from pathlib import Path

import yaml

FICHES_DIR = Path(__file__).resolve().parents[1] / "config" / "fiches"

# Acronymes de sources / jargon retirés des libellés affichés (`nom:`).
# Recherche en sous-chaîne insensible à la casse, mais on garde des formes
# précises pour éviter les faux positifs (ex. "API" présent dans aucun nom).
NOMS_INTERDITS = [
    "NOAA",
    "WASDE",
    "stocks-to-use",
    "CFTC COT",
    "COT ",
    "COMEX",
    "SHFE",
    "DXY",
    "GATE",
    "GASC",
    "EUDR",
    "NASS",
    "FedWatch",
    "Caixin",
    "drought",
    "Forward P/E",
    "bull-bear",
]


def _tous_les_noms():
    """Yield (fiche, critere_id, nom) pour chaque critère de chaque fiche."""
    for path in sorted(FICHES_DIR.glob("*.yml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for crit in data.get("criteres", []):
            nom = crit.get("nom")
            if nom is not None:
                yield (path.stem, crit.get("id"), nom)


def test_aucun_acronyme_source_dans_les_noms():
    """Aucun libellé `nom:` ne contient un acronyme de source retiré."""
    fautes = []
    for fiche, cid, nom in _tous_les_noms():
        for interdit in NOMS_INTERDITS:
            if interdit.lower() in nom.lower():
                fautes.append(f"{fiche} #{cid} : « {nom} » contient « {interdit} »")
    assert not fautes, "Acronymes non traduits trouvés :\n" + "\n".join(fautes)


def test_ble_noaa_traduit():
    """La fiche blé ne contient plus « NOAA » mais le libellé clair de sécheresse."""
    data = yaml.safe_load((FICHES_DIR / "ble.yml").read_text(encoding="utf-8"))
    noms = [c["nom"] for c in data["criteres"]]
    assert all("NOAA" not in n for n in noms)
    assert "Sécheresse dans les plaines céréalières US" in noms


def test_cot_traduit_en_gros_speculateurs():
    """Le critère COT or est devenu « Positionnement des gros spéculateurs (or) »."""
    data = yaml.safe_load((FICHES_DIR / "or.yml").read_text(encoding="utf-8"))
    par_cle = {c["cle_courante"]: c["nom"] for c in data["criteres"]}
    assert par_cle["cftc_cot_nets"] == "Positionnement des gros spéculateurs (or)"


def test_glossaire_acronymes_conserves_present():
    """Le glossaire d'aide cite bien les acronymes volontairement conservés."""
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import scoring_analyste

    glossaire = "\n".join(scoring_analyste.DETAIL_TABLE_GLOSSARY_LINES)
    for terme in ("PMI", "RSI", "VIX", "SKEW", "VVIX"):
        assert terme in glossaire
