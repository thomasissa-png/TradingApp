"""Re-découpage par familles de vitesse (fondateur 30/06) : un signal ne pèse sur le
24h que s'il peut bouger le prix le jour même. Verrou des invariants clés sur les
15 fiches. (Les signaux news/régime/événements sont volontairement LAISSÉS tels quels.)
"""
import glob
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def _criteres():
    for f in sorted(glob.glob(str(ROOT / "config" / "fiches" / "*.yml"))):
        if os.path.basename(f).startswith("_"):
            continue
        d = yaml.safe_load(open(f, encoding="utf-8"))
        for c in d.get("criteres", []):
            yield os.path.basename(f), c


def test_meteo_zero_sur_24h():
    """La météo agit sur des semaines → 0 sur le 24h, pleine sur le 1m."""
    for fic, c in _criteres():
        cle = c.get("cle_courante", "")
        if cle.startswith("meteo_") or cle.startswith("noaa") or "drought" in cle:
            p = c.get("pertinence", {})
            assert p.get("24h") == 0.0, f"{fic}:{cle} météo doit être 0 sur 24h ({p})"
            assert p.get("1m", 0) >= 0.9, f"{fic}:{cle} météo doit servir le 1m"


def test_momentum_20j_quasi_nul_sur_24h_et_7j_mene():
    """Sur le 24h : la tendance 20j est minoritaire (<=0.1) et la 7j la domine."""
    by_actif = {}
    for fic, c in _criteres():
        cle = c.get("cle_courante", "")
        if cle.startswith("momentum_prix_20j_"):
            by_actif.setdefault(cle.replace("20j", ""), {})["20j"] = c["pertinence"]["24h"]
        if cle.startswith("momentum_prix_7j_"):
            by_actif.setdefault(cle.replace("7j", ""), {})["7j"] = c["pertinence"]["24h"]
    assert by_actif, "aucun momentum trouvé"
    for base, d in by_actif.items():
        if "20j" in d:
            assert d["20j"] <= 0.1, f"{base}20j doit être <=0.1 sur 24h (got {d['20j']})"
        if "20j" in d and "7j" in d:
            assert d["7j"] > d["20j"], f"{base}: 7j ({d['7j']}) doit mener vs 20j ({d['20j']}) sur 24h"


def test_cot_positionnement_hebdo_quasi_nul_sur_24h():
    """Le positionnement COT (hebdo, en retard) ne pilote pas une séance."""
    for fic, c in _criteres():
        if c.get("cle_courante", "").startswith("cftc_cot"):
            assert c["pertinence"]["24h"] <= 0.1, f"{fic} COT doit être <=0.1 sur 24h"


def test_news_et_regime_non_demotes_sur_24h():
    """Garde-fou : on n'a PAS cassé le signal du jour — au moins un signal news
    (triplet) ou régime de risque reste fort (>=0.7) sur le 24h sur l'univers."""
    forts_24h = [
        c.get("cle_courante", "")
        for _, c in _criteres()
        if c.get("normalisation") == "triplet" and c.get("pertinence", {}).get("24h", 0) >= 0.7
    ]
    assert forts_24h, "aucun porteur de news fort sur 24h : le signal du jour a été cassé !"
